# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# 文件名: {检测标签移动图片}.py
# 功能: {如果使用爬虫等工具获取图片，可能或爬取到一些无关数据，因此可以使用本程序筛选有效数据，或者是筛选目标数据}
# 作者: {Emilison_Black}
# 创建日期: {2025年2月16日}
# 最后修改日期: {2025年2月17日}
# 版本: {V1.0}
# ----------------------------------------------------------------------------
# 免责声明：
# 本软件按"原样"提供，不提供任何形式的明示或暗示保证，包括但不限于对适销性、
# 特定用途适用性和非侵权性的保证。作者或版权持有人不对任何直接、间接、偶发、
# 特殊、示范性或 consequential 损害（包括但不限于替代商品或服务的采购、使用损失、
# 数据或业务中断）承担责任，即使已被告知可能发生此类损害。
# 联系信息：
#  - 邮箱: {2774177348@qq.com | emls2774177348@gmail.com |}
#  - GitHub: {https://github.com/EmilisonBlack}
#  - B站: {https://space.bilibili.com/391271832?spm_id_from=333.1007.0.0}
# 致谢：
#  - {OpenAi DeepSeek 通义千问}
#  - {挂科边缘毕业版} (https://space.bilibili.com/1595729670)
#
# 更新日志：
# ----------------------------------------------------------------------------

import os
import sys
import logging
import warnings
import cv2
import torch
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import shutil
from ultralytics import YOLO
from multiprocessing import get_context, Manager
from tqdm import tqdm
import numpy as np
import psutil
import time
import gc  # 用于垃圾回收
import math

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("image_processor.log"),
        logging.StreamHandler()
    ]
)

warnings.filterwarnings("ignore", category=UserWarning, module="torchvision.io.image")

##############################################################################
#                            配置参数（按需修改）                             #
##############################################################################

MODEL_PATH = "/weights/best.pt"  # 模型路径
DESTINATION_FOLDER = "打标文件/images"  # 目标文件夹路径
SUPPORTED_IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".bmp"}  # 支持的图片格式
CONFIDENCE_THRESHOLD = 0.1  # 置信度阈值 (0-1)
MAX_WORKERS = 12  # 最大并行进程数
BATCH_SIZE = 64  # 每批次处理图片数
MEMORY_LIMIT_GB = 24  # 内存限制（GB）
GPU_MEMORY_LIMIT = 0.8  # GPU显存使用上限

##############################################################################

class ImageProcessor:
    def __init__(self):
        self.target_classes = {}
        self.ctx = get_context('spawn')
        self.manager = Manager()
        self.total_images = 0
        self.moved_count = 0

    class MemoryController:
        """内存监控器"""
        def __init__(self):
            self.process = psutil.Process(os.getpid())

        @property
        def used_memory_gb(self):
            return self.process.memory_info().rss / (1024 ** 3)

        def is_memory_safe(self):
            system_mem = psutil.virtual_memory().percent < 90
            process_mem = self.used_memory_gb < MEMORY_LIMIT_GB * 0.9
            return system_mem and process_mem

    def _get_user_input(self):
        """获取用户输入（严格验证）"""
        root = tk.Tk()
        root.title("选择标签和数量")

        # 获取模型类别（不加载完整模型）
        try:
            model_info = YOLO(MODEL_PATH, verbose=False).names
            class_names = list(model_info.values())
            del model_info  # 及时释放资源
        except Exception as e:
            messagebox.showerror("错误", f"模型信息获取失败: {str(e)}")
            sys.exit(1)

        # 创建一个字典来存储标签和对应的数字
        target_classes = {}

        # 创建标签和数字输入框
        for class_name in class_names:
            frame = tk.Frame(root)
            frame.pack(fill=tk.X, padx=5, pady=5)

            label = tk.Label(frame, text=class_name)
            label.pack(side=tk.LEFT)

            var = tk.IntVar(value=0)
            spinbox = tk.Spinbox(frame, from_=0, to=100, textvariable=var)
            spinbox.pack(side=tk.RIGHT)

            target_classes[class_name] = var

        def on_confirm():
            """确认按钮点击事件"""
            for class_name, var in target_classes.items():
                if var.get() > 0:
                    self.target_classes[class_name] = var.get()
            root.destroy()

        confirm_button = tk.Button(root, text="确定", command=on_confirm)
        confirm_button.pack(pady=10)

        src_folder = filedialog.askdirectory(title="选择图片文件夹")
        root.mainloop()

        if not src_folder:
            logging.info("操作已取消")
            sys.exit(0)

        return src_folder

    @staticmethod
    def _worker_init(target_classes: dict):
        """
        独立进程初始化，加载模型、配置GPU资源，并将目标类别保存到模型实例上
        """
        global worker_model
        try:
            # 初始化CUDA上下文
            if torch.cuda.is_available():
                torch.cuda.init()
                torch.cuda.empty_cache()
                torch.cuda.set_per_process_memory_fraction(GPU_MEMORY_LIMIT)

            # 加载模型
            worker_model = YOLO(MODEL_PATH, verbose=False)
            if torch.cuda.is_available():
                worker_model.to('cuda')
            worker_model.fuse()

            # 将目标类别传递给模型实例（后续检测时使用）
            worker_model.target_classes = target_classes

            # 验证类别兼容性
            model_classes = list(worker_model.names.values())
            missing = [k for k in target_classes if k not in model_classes]
            if missing:
                logging.error(f"模型缺少所需类别: {missing}")
                sys.exit(1)

        except Exception as e:
            logging.critical(f"进程初始化失败: {str(e)}")
            sys.exit(1)

    @staticmethod
    def _process_batch(batch: list) -> list:
        """
        批量处理函数，处理一批图片并返回符合要求的文件路径列表
        检测逻辑：
          1. 读取图片并调用模型检测。
          2. 对于每个图片，统计目标类别（worker_model.target_classes 中指定的）的检测数量。
          3. 如果任一目标类别的检测数量大于等于用户指定的最小数量，则返回该图片路径。
        """
        move_files = []
        try:
            for img_path in batch:
                try:
                    img = cv2.imread(img_path)
                    if img is None:
                        continue

                    # 使用模型检测
                    results = worker_model(img, imgsz=640, verbose=False)

                    # 初始化计数器，仅计数目标类别
                    counts = {k: 0 for k in worker_model.target_classes}

                    if results and results[0].boxes is not None:
                        detections = results[0].boxes.data.cpu().numpy()
                        for det in detections:
                            # 检查检测结果数据是否合法
                            if len(det) < 6:
                                continue
                            *_, conf, cls_id = det
                            cls_name = worker_model.names.get(int(cls_id), "")
                            # 只计数目标类别且满足置信度要求的检测
                            if cls_name in worker_model.target_classes and conf >= CONFIDENCE_THRESHOLD:
                                counts[cls_name] += 1

                    # 判断是否满足用户要求的目标类别数
                    valid = any(counts.get(tc, 0) >= worker_model.target_classes[tc] for tc in worker_model.target_classes)
                    if valid:
                        move_files.append(img_path)

                except Exception as e:
                    logging.error(f"处理失败 {os.path.basename(img_path)}: {str(e)}")
                finally:
                    if 'img' in locals():
                        del img
            # 每批次结束后清理内存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
        except Exception as e:
            logging.error(f"批处理失败: {str(e)}")
        return move_files

    def _iter_image_batches(self, src_folder: str, batch_size: int):
        """
        利用生成器按批次读取目录中的图片路径，避免一次性加载所有文件
        """
        batch = []
        with os.scandir(src_folder) as it:
            for entry in it:
                if entry.is_file() and os.path.splitext(entry.name)[1].lower() in SUPPORTED_IMAGE_FORMATS:
                    batch.append(entry.path)
                    if len(batch) >= batch_size:
                        yield batch
                        batch = []
            if batch:
                yield batch

    def _count_total_images(self, src_folder: str) -> int:
        """仅扫描目录以计算符合扩展名的图片数量"""
        count = 0
        with os.scandir(src_folder) as it:
            for entry in it:
                if entry.is_file() and os.path.splitext(entry.name)[1].lower() in SUPPORTED_IMAGE_FORMATS:
                    count += 1
        return count

    def run(self):
        """主运行流程"""
        # 获取用户输入（目标类别与源文件夹）
        src_folder = self._get_user_input()
        logging.info(f"\n{'=' * 40}\n启动图片处理任务\n"
                     f"源文件夹: {src_folder}\n"
                     f"目标类别: {self.target_classes}\n"
                     f"内存限制: {MEMORY_LIMIT_GB}GB\n"
                     f"并行进程: {MAX_WORKERS}\n{'=' * 40}")

        # 统计符合扩展名的图片总数（仅统计，不加载图像数据）
        self.total_images = self._count_total_images(src_folder)
        if self.total_images == 0:
            logging.warning("未找到符合格式的图片！")
            return

        total_batches = math.ceil(self.total_images / BATCH_SIZE)
        logging.info(f"共计{self.total_images}张图片，分为{total_batches}批次处理。")

        # 创建图片批次生成器（惰性加载，内存占用小）
        batch_generator = self._iter_image_batches(src_folder, BATCH_SIZE)

        # 使用独立上下文管理进程池，利用 imap_unordered 逐批处理
        with self.ctx.Pool(
                processes=MAX_WORKERS,
                initializer=self._worker_init,
                initargs=(self.target_classes,)
        ) as pool:

            pbar_batches = tqdm(total=total_batches, desc="处理批次", unit="batch")
            pbar_move = tqdm(total=self.total_images, desc="移动图片", unit="file")

            for batch_result in pool.imap_unordered(self._process_batch, batch_generator, chunksize=1):
                while not self.MemoryController().is_memory_safe():
                    logging.warning("主进程内存使用过高，暂停提交任务...")
                    time.sleep(5)

                for src_path in batch_result:
                    try:
                        dest_path = os.path.join(DESTINATION_FOLDER, os.path.basename(src_path))
                        shutil.move(src_path, dest_path)
                        self.moved_count += 1
                    except Exception as e:
                        logging.error(f"移动失败: {os.path.basename(src_path)} - {str(e)}")
                    finally:
                        pbar_move.update(1)
                pbar_batches.update(1)
                gc.collect()

            pbar_batches.close()
            pbar_move.close()

        # 生成报告
        success_rate = self.moved_count / self.total_images * 100 if self.total_images > 0 else 0
        logging.info(
            f"\n{'=' * 40}\n"
            f"处理完成！\n"
            f"总图片数: {self.total_images}\n"
            f"成功移动: {self.moved_count}\n"
            f"成功率: {success_rate:.2f}%\n"
            f"{'=' * 40}"
        )


if __name__ == "__main__":
    try:
        processor = ImageProcessor()
        processor.run()
    except Exception as e:
        logging.critical(f"程序崩溃: {str(e)}", exc_info=True)
        sys.exit(1)
