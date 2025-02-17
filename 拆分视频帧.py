# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# 文件名: {拆分视频帧}.py
# 功能: {在寻找训练集的过程中，为了弥补图片实例的不足，我们可能需要用到视频帧来充当训练数据，此代码用于从视频中截取图片}
# 作者: {Emilison_Black}
# 创建日期: {2025年2月15日}
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

"""请修改输入和输出文件目录"""

import os
import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from multiprocessing import Process, Queue, cpu_count, Pool, Manager
from multiprocessing.managers import BaseManager  # 导入 Empty 异常
from queue import Empty  # 从 queue 模块导入 Empty 异常
import time


class VideoExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("视频分解工具")
        self.root.geometry("750x750")

        # 直接在代码中设置输入和输出文件夹路径
        self.input_folder = "Cache"  # 用户修改为输入文件夹路径
        self.output_folder = "pictures"  # 用户修改为输出文件夹路径

        # 初始化参数
        self.img_format = tk.StringVar(value="jpg")  # 图片格式
        self.running = False

        # 自动创建输出文件夹
        os.makedirs(self.output_folder, exist_ok=True)

        self.setup_ui()

    def setup_ui(self):
        # GUI布局
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 输入文件夹信息
        input_frame = ttk.LabelFrame(main_frame, text="输入文件夹", padding=(15, 10))
        input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(input_frame, text=f"输入文件夹路径: {self.input_folder}").pack(anchor=tk.W)

        # 输出文件夹信息
        output_frame = ttk.LabelFrame(main_frame, text="输出文件夹", padding=(15, 10))
        output_frame.pack(fill=tk.X, pady=5)

        ttk.Label(output_frame, text=f"输出文件夹路径: {self.output_folder}").pack(anchor=tk.W)

        # 视频文件列表
        self.video_list_frame = ttk.LabelFrame(main_frame, text="检测到的视频文件", padding=(15, 10))
        self.video_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.video_list = tk.Listbox(self.video_list_frame, height=10, selectmode=tk.SINGLE)
        self.video_list.pack(fill=tk.BOTH, expand=True)

        # 参数设置
        param_frame = ttk.LabelFrame(main_frame, text="参数设置", padding=(15, 10))
        param_frame.pack(fill=tk.X, pady=5)

        ttk.Label(param_frame, text="图片格式:").grid(row=0, column=2, padx=5)
        ttk.Combobox(param_frame, textvariable=self.img_format, values=("jpg", "png", "bmp"), width=8).grid(row=0,
                                                                                                           column=3)

        # 进度条和日志
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, pady=10)

        self.log_text = tk.Text(main_frame, height=10, state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 操作按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        self.start_btn = ttk.Button(btn_frame, text="开始分解", command=self.start_process)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.cancel_process).pack(side=tk.LEFT)

        # 初始化视频文件列表
        self.update_video_list()

    def update_video_list(self):
        """更新视频文件列表"""
        self.video_list.delete(0, tk.END)
        video_files = [
            f for f in os.listdir(self.input_folder)
            if os.path.splitext(f)[1].lower() in ('.mp4', '.avi', '.mov')
        ]
        for video_file in video_files:
            self.video_list.insert(tk.END, video_file)

    def start_process(self):
        if not self.input_folder or not self.output_folder:
            messagebox.showwarning("警告", "请先设置输入和输出文件夹路径！")
            return

        if self.running:
            messagebox.showinfo("提示", "任务已在运行中！")
            return

        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.progress['value'] = 0
        self.log_message("\n=== 开始处理视频 ===")

        # 获取视频文件列表
        video_files = [self.video_list.get(i) for i in range(self.video_list.size())]
        total_videos = len(video_files)
        self.log_message(f"找到 {total_videos} 个视频文件")
        self.log_message(f"视频文件列表: {video_files}")  # 调试信息

        # 限制并发进程数为 CPU 核心数的一半
        max_processes = max(4, 6)
        pool = Pool(processes=max_processes)

        # 使用Manager的Queue
        manager = Manager()
        queue = manager.Queue()

        # 启动进程
        for video_file in video_files:
            pool.apply_async(extract_frames, args=(video_file, self.input_folder, self.output_folder, self.img_format.get(), queue))

        # 更新进度条和日志
        completed = 0
        while completed < total_videos:
            try:
                message = queue.get(timeout=1)  # 添加超时机制
                if message == "DONE":
                    completed += 1
                    self.progress['value'] = completed / total_videos * 100
                else:
                    self.log_message(message)
            except Empty:  # 使用 multiprocessing.managers.Empty
                # 适当等待，避免占用过多CPU
                self.root.update()
                continue

        pool.close()
        pool.join()

        # 移动处理过的视频到新文件夹
        self.move_processed_videos(video_files)

        self.log_message("\n=== 所有视频处理完成 ===")
        self.running = False
        self.start_btn.config(state=tk.NORMAL)

    def move_processed_videos(self, video_files):
        """将处理过的视频移动到新文件夹"""
        run_count = 1
        while os.path.exists(os.path.join(self.input_folder, str(run_count))):
            run_count += 1

        new_folder = os.path.join(self.input_folder, str(run_count))
        os.makedirs(new_folder, exist_ok=True)

        for video_file in video_files:
            src = os.path.join(self.input_folder, video_file)
            dst = os.path.join(new_folder, video_file)
            os.rename(src, dst)
            self.log_message(f"移动文件: {video_file} -> {new_folder}")

    def cancel_process(self):
        self.running = False
        self.log_message("\n× 任务已取消！")

    def log_message(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)


def extract_frames(video_file, input_folder, output_folder, img_format, queue):
    try:
        video_path = os.path.join(input_folder, video_file)
        queue.put(f"\n正在处理: {video_file}")
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            queue.put(f"  × 无法打开视频文件")
            queue.put("DONE")  # 确保发送DONE信号
            return

        # 获取视频参数
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps  # 视频时长（秒）
        queue.put(f"  - 帧率: {fps:.2f}, 总帧数: {total_frames}, 时长: {duration:.2f}秒")

        # 根据视频时长动态计算拆分帧数
        if duration < 60:  # <1分钟
            total_frames_to_extract = 10
        elif duration <= 300:  # 1-5分钟
            total_frames_to_extract = int(10 + (duration - 60) * 0.2)
        else:  # >5分钟
            total_frames_to_extract = 100

        # 计算帧间隔
        interval = max(1, int(total_frames / total_frames_to_extract))
        queue.put(f"  - 拆分帧数: {total_frames_to_extract}, 帧间隔: {interval}")

        frame_count = 0
        saved_count = 0

        while True:
            ret = cap.grab()
            if not ret:
                break

            if frame_count % interval == 0:
                ret, frame = cap.retrieve()
                if not ret or frame is None:
                    queue.put(f"  × 帧数据为空，跳过保存")
                    continue

                output_path = os.path.join(
                    output_folder,
                    f"{os.path.splitext(video_file)[0]}_frame{frame_count}.{img_format}"
                )
                queue.put(f"  保存路径: {output_path}")

                try:
                    success = cv2.imwrite(output_path, frame)
                    if success:
                        saved_count += 1
                    else:
                        queue.put(f"  × 保存失败: 文件未写入")
                except Exception as e:
                    queue.put(f"  × 保存失败: {str(e)}")

            frame_count += 1
        cap.release()
        queue.put(f"  √ 保存 {saved_count} 张图片")
        queue.put("DONE")
    except Exception as e:
        queue.put(f"\n× 发生错误: {str(e)}")
        queue.put("DONE")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoExtractorApp(root)
    root.mainloop()
