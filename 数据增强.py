# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# 文件名: {数组增强}.py
# 功能: {在训练数据量过少或数据质量过于统一的情况下，本代码可以成倍增加数据量，同时引入了旋转，添加噪声，水平和垂直翻转功能。并保证对应TXT标记框仍然能锁住标记对象}
# 作者: {Emilison_Black}
# 创建日期: {2025年2月17日}
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



#///注意，文件名称和路径不能含有中文和特殊字符（例如空格）/// ///注意，文件名称和路径不能含有中文和特殊字符（例如空格）///
#///注意，文件名称和路径不能含有中文和特殊字符（例如空格）/// ///注意，文件名称和路径不能含有中文和特殊字符（例如空格）///
#///注意，文件名称和路径不能含有中文和特殊字符（例如空格）/// ///注意，文件名称和路径不能含有中文和特殊字符（例如空格）///



import os
import random
import logging
import cv2
import numpy as np
from pathlib import Path
from tkinter import Tk, filedialog, Label, Button, StringVar, Entry, messagebox

# ====================== 日志配置 ======================
logging.basicConfig(
    filename="enhancement.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ====================== 坐标系转换工具 ======================
class CoordinateSystem:
    @staticmethod
    def yolo_to_pixel(bbox, img_width, img_height):
        """将YOLO格式的归一化坐标转换为画布上的像素坐标（支持多边形顶点）"""
        x_center, y_center, w, h = bbox
        # 计算原始图像上的绝对坐标（基于画布中心）
        x = x_center * img_width
        y = y_center * img_height
        # 计算包围盒的四个顶点坐标|数据是像素坐标
        half_w = w * img_width / 2
        half_h = h * img_height / 2
        return [
            (x - half_w, y - half_h),  # 左上
            (x + half_w, y - half_h),  # 右上
            (x + half_w, y + half_h),  # 右下
            (x - half_w, y + half_h)  # 左下
        ]

    @staticmethod
    def pixel_to_yolo(polygon, img_width, img_height):
        """把像素坐标转换成YOLO坐标，外接四边形"""
        all_x = [p[0] for p in polygon]
        all_y = [p[1] for p in polygon]

        # 计算多边形的边界框
        min_x = min(all_x)
        max_x = max(all_x)
        min_y = min(all_y)
        max_y = max(all_y)

        # 计算中心点
        x_center = (min_x + max_x) / 2
        y_center = (min_y + max_y) / 2

        # 计算宽度和高度
        width = max_x - min_x
        height = max_y - min_y

        # 转换到相对坐标系
        x_center_rel = max(0.0, min(1.0, x_center / img_width))
        y_center_rel = max(0.0, min(1.0, y_center / img_height))
        width_rel = max(0.0, min(1.0, width / img_width))
        height_rel = max(0.0, min(1.0, height / img_height))

        return [x_center_rel, y_center_rel, width_rel, height_rel]


# ====================== 图像变换引擎 ======================
class CanvasOperator:
    def __init__(self, image_path):
        # 初始化原始图像
        self.original = cv2.imread(str(image_path))
        if self.original is None:
            raise ValueError(f"无法加载图像: {image_path}")

        self.height, self.width = self.original.shape[:2]

        # 存储标注框多边形（每个元素是包含4个顶点的列表）
        self.polygons = []

    def load_annotations(self, txt_path):
        """加载YOLO格式标注并转换为多边形顶点"""
        logging.debug(f"Loading annotations from: {txt_path}")
        if not Path(txt_path).exists():
            logging.warning(f"Annotation file not found: {txt_path}")
            return

        with open(txt_path, 'r') as f:
            for line in f:
                try:
                    cls_id, x_center, y_center, width, height = list(map(float, line.strip().split()))
                    logging.debug(
                        f"Loaded annotation: class={cls_id}, x_center={x_center}, y_center={y_center}, width={width}, height={height}"
                    )

                    # 将归一化坐标转换为像素坐标
                    x_center *= self.width
                    y_center *= self.height
                    width *= self.width
                    height *= self.height

                    # 计算包围盒的四个顶点坐标|数据是像素坐标
                    half_w = width / 2
                    half_h = height / 2
                    x1 = x_center - half_w
                    y1 = y_center - half_h
                    x2 = x_center + half_w
                    y2 = y_center - half_h
                    x3 = x_center + half_w
                    y3 = y_center + half_h
                    x4 = x_center - half_w
                    y4 = y_center + half_h

                    # 将顶点坐标添加到多边形列表|至此都是水平坐标
                    polygon = [
                        (x1, y1),  # 左上
                        (x2, y2),  # 右上
                        (x3, y3),  # 右下
                        (x4, y4)  # 左下
                    ]
                    self.polygons.append((int(cls_id), polygon))
                except Exception as e:
                    logging.error(f"Failed to parse annotation line: {line.strip()}, error: {str(e)}")

    def rotate_image(self, angle):
        # 计算旋转中心
        center = (self.width // 2, self.height // 2)

        # 获取旋转矩阵
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

        # 执行旋转
        rotated_image = cv2.warpAffine(
            self.original, rotation_matrix, (self.width, self.height),
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255)
        )

        # 更新多边形坐标
        new_polygons = []
        for cls_id, polygon in self.polygons:
            new_polygon = []
            for (x, y) in polygon:
                # 应用旋转矩阵
                point = np.array([x, y, 1]).reshape(-1, 1, 3)
                transformed_point = cv2.transform(point, rotation_matrix).squeeze()
                new_polygon.append(tuple(transformed_point))

            new_polygons.append((cls_id, new_polygon))

        self.original = rotated_image
        self.polygons = new_polygons

    def horizontal_flip(self):
        # 水平翻转图像
        self.original = cv2.flip(self.original, 1)

        # 更新多边形坐标
        for i, (cls_id, polygon) in enumerate(self.polygons):
            new_polygon = [(self.width - x, y) for (x, y) in polygon]
            self.polygons[i] = (cls_id, new_polygon)

    def vertical_flip(self):
        # 垂直翻转图像
        self.original = cv2.flip(self.original, 0)

        # 更新多边形坐标
        for i, (cls_id, polygon) in enumerate(self.polygons):
            new_polygon = [(x, self.height - y) for (x, y) in polygon]
            self.polygons[i] = (cls_id, new_polygon)

    def add_noise(self):
        noise = np.random.normal(0, 25, self.original.shape).astype(np.int32)
        noisy_img = np.clip(self.original + noise, 0, 255).astype(np.uint8)
        self.original = noisy_img


# ====================== 增强流水线 ======================
class EnhancementPipeline:
    @staticmethod
    def apply_rotation(canvas_operator, angle):
        """旋转增强"""
        canvas_operator.rotate_image(angle)
        logging.debug(f"Applied rotation: {angle:.2f} degrees")
        return canvas_operator

    @staticmethod
    def apply_horizontal_flip(canvas_operator):
        """水平翻转增强"""
        canvas_operator.horizontal_flip()
        logging.debug("Applied horizontal flip")
        return canvas_operator

    @staticmethod
    def apply_vertical_flip(canvas_operator):
        """垂直翻转增强"""
        canvas_operator.vertical_flip()
        logging.debug("Applied vertical flip")
        return canvas_operator

    @staticmethod
    def apply_noise(canvas_operator):
        """添加噪声增强"""
        canvas_operator.add_noise()
        logging.debug("Added Gaussian noise")
        return canvas_operator


# ====================== 主程序逻辑 ======================
class EnhancementCore:
    def __init__(self, input_folder, output_folder, probabilities, min_aug, max_aug):
        self.input_dir = Path(input_folder)
        self.output_dir = Path(output_folder) / "enhanced"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.probabilities = probabilities
        self.min_aug = min_aug
        self.max_aug = max_aug

    def process_image(self, img_path):
        """处理单张图像"""
        original_image = cv2.imread(str(img_path))
        if original_image is None:
            logging.error(f"无法加载图像: {img_path}")
            return

        canvas = CanvasOperator(img_path)
        txt_path = img_path.with_suffix('.txt')
        if txt_path.exists():
            canvas.load_annotations(txt_path)

        num_augmentations = random.randint(self.min_aug, self.max_aug)  # 随机选择min_aug到max_aug种增强方式
        operations = ['rotate', 'horizontal_flip', 'vertical_flip', 'add_noise']

        # 使用 choices 允许重复选择
        selected_operations = random.choices(operations, k=num_augmentations)

        for i in range(num_augmentations):
            augmented_canvas = CanvasOperator(img_path)  # 创建一个新的CanvasOperator实例
            augmented_canvas.original = original_image.copy()  # 复制原始图像
            augmented_canvas.polygons = canvas.polygons.copy()  # 复制标注信息

            for operation in selected_operations:
                if operation == 'rotate' and random.random() < self.probabilities['rotate']:
                    angle = random.uniform(-45, 45)
                    EnhancementPipeline.apply_rotation(augmented_canvas, angle)
                elif operation == 'horizontal_flip' and random.random() < self.probabilities['horizontal_flip']:
                    EnhancementPipeline.apply_horizontal_flip(augmented_canvas)
                elif operation == 'vertical_flip' and random.random() < self.probabilities['vertical_flip']:
                    EnhancementPipeline.apply_vertical_flip(augmented_canvas)
                elif operation == 'add_noise' and random.random() < self.probabilities['add_noise']:
                    EnhancementPipeline.apply_noise(augmented_canvas)

            # 保存结果
            logging.debug("Saving results")
            self.save_results(img_path, augmented_canvas.original, augmented_canvas.polygons, i + 1)

    def save_results(self, orig_path, image, polygons, aug_index):
        try:
            base_stem = orig_path.stem
            img_ext = orig_path.suffix
            stem = f"{base_stem}_aug{aug_index}"
            img_save_path = self.output_dir / f"{stem}{img_ext}"
            txt_save_path = self.output_dir / f"{stem}.txt"

            # 保存图像
            if not cv2.imwrite(str(img_save_path), image):
                raise IOError("Failed to write image file")

            # 保存标注
            with open(txt_save_path, 'w') as f:
                for cls_id, polygon in polygons:
                    yolo_bbox = CoordinateSystem.pixel_to_yolo(polygon, image.shape[1], image.shape[0])
                    f.write(f"{int(cls_id)} " + " ".join(f"{v:.6f}" for v in yolo_bbox) + "\n")

        except Exception as e:
            logging.error(f"保存失败: {str(e)}")
            if img_save_path.exists():
                img_save_path.unlink()
            if txt_save_path.exists():
                txt_save_path.unlink()
            raise

    def batch_process(self):
        """批量处理整个文件夹"""
        count = 0
        logging.info(f"Input directory: {self.input_dir}")
        logging.info(f"Files in input directory: {list(self.input_dir.glob('*'))}")

        for img_file in self.input_dir.glob("*"):
            if img_file.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
                logging.info(f"Skipping non-image file: {img_file.name}")
                continue
            logging.info(f"Processing image: {img_file.name}")
            self.process_image(img_file)
            count += 1
            logging.info(f"Processed {img_file.name} ({count} total)")
        return count


# ====================== GUI界面 ======================
class EnhancementGUI:
    def __init__(self, master):
        self.master = master
        master.title("智能图像增强工具 v1.0")
        master.geometry("500x500")

        # 控件变量
        self.input_folder = StringVar()
        self.prob_rotate = StringVar(value="0.75")
        self.prob_horizontal_flip = StringVar(value="0.5")
        self.prob_vertical_flip = StringVar(value="0.75")
        self.prob_add_noise = StringVar(value="0.65")
        self.min_aug = StringVar(value="2")
        self.max_aug = StringVar(value="3")

        # 界面布局
        Label(master, text="输入文件夹").pack(pady=5)
        Button(master, text="浏览", command=self.select_input).pack()
        Label(master, textvariable=self.input_folder).pack()

        Label(master, text="旋转概率").pack(pady=5)
        Entry(master, textvariable=self.prob_rotate).pack()

        Label(master, text="水平翻转概率").pack(pady=5)
        Entry(master, textvariable=self.prob_horizontal_flip).pack()

        Label(master, text="垂直翻转概率").pack(pady=5)
        Entry(master, textvariable=self.prob_vertical_flip).pack()

        Label(master, text="添加噪声概率").pack(pady=5)
        Entry(master, textvariable=self.prob_add_noise).pack()

        Label(master, text="最小增强数量").pack(pady=5)
        Entry(master, textvariable=self.min_aug).pack()

        Label(master, text="最大增强数量").pack(pady=5)
        Entry(master, textvariable=self.max_aug).pack()

        Button(master, text="开始增强", command=self.start_process).pack(pady=15)
        self.status = Label(master, text="就绪", fg="green")
        self.status.pack()

    def select_input(self):
        path = filedialog.askdirectory()
        if path:
            self.input_folder.set(path)

    def start_process(self):
        """启动增强流程"""
        input_path = Path(self.input_folder.get())
        probabilities = {
            'rotate': float(self.prob_rotate.get()),
            'horizontal_flip': float(self.prob_horizontal_flip.get()),
            'vertical_flip': float(self.prob_vertical_flip.get()),
            'add_noise': float(self.prob_add_noise.get())
        }
        min_aug = int(self.min_aug.get())
        max_aug = int(self.max_aug.get())
        core = EnhancementCore(input_path, input_path, probabilities, min_aug, max_aug)
        total = core.batch_process()
        messagebox.showinfo("完成", f"成功增强 {total} 张图像！")
        self.status.config(text=f"完成：{total} 张已处理")


if __name__ == "__main__":
    root = Tk()
    app = EnhancementGUI(root)
    root.mainloop()
