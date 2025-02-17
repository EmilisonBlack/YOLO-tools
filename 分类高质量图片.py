# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# 文件名: {分类高质量图片}.py
# 功能: {将数据集中的高质量与低质量图片分开，分隔标准为有效像素数。选择一个文件夹，输入分隔阈值，运行程序后，选中目录下将会创建出2个文件夹。
# 低于阈值的图片将会被划入低质量图片，否则存入高质量文件夹}
# 作者: {Emilison_Black}
# 创建日期: {2025年2月13日}
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
import shutil
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox
from PIL import Image

# 创建GUI界面
class ImageClassifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片分类器")
        self.root.geometry("400x200")

        # 输入阈值
        self.label_threshold = Label(root, text="输入像素阈值（例如 1000000）：")
        self.label_threshold.pack(pady=10)
        self.entry_threshold = Entry(root)
        self.entry_threshold.pack(pady=5)

        # 选择文件夹按钮
        self.button_select_folder = Button(root, text="选择文件夹", command=self.select_folder)
        self.button_select_folder.pack(pady=10)

        # 执行分类按钮
        self.button_classify = Button(root, text="开始分类", command=self.classify_images)
        self.button_classify.pack(pady=10)

        # 初始化文件夹路径
        self.folder_path = None

    # 选择文件夹
    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            messagebox.showinfo("文件夹已选择", f"已选择文件夹：{self.folder_path}")

    # 分类图片
    def classify_images(self):
        if not self.folder_path:
            messagebox.showerror("错误", "请先选择一个文件夹！")
            return

        threshold = self.entry_threshold.get()
        if not threshold.isdigit():
            messagebox.showerror("错误", "请输入有效的像素阈值！")
            return
        threshold = int(threshold)

        # 创建高质量和低质量文件夹
        high_quality_folder = os.path.join(self.folder_path, "高质量图片")
        low_quality_folder = os.path.join(self.folder_path, "低质量图片")
        os.makedirs(high_quality_folder, exist_ok=True)
        os.makedirs(low_quality_folder, exist_ok=True)

        # 遍历文件夹中的图片
        for filename in os.listdir(self.folder_path):
            file_path = os.path.join(self.folder_path, filename)
            if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                try:
                    # 打开图片并获取像素信息
                    with Image.open(file_path) as img:
                        width, height = img.size
                        total_pixels = width * height

                    # 根据阈值移动图片
                    if total_pixels >= threshold:
                        shutil.move(file_path, os.path.join(high_quality_folder, filename))
                    else:
                        shutil.move(file_path, os.path.join(low_quality_folder, filename))
                except Exception as e:
                    print(f"无法处理图片 {filename}: {e}")

        messagebox.showinfo("完成", "图片分类完成！")

# 运行程序
if __name__ == "__main__":
    root = Tk()
    app = ImageClassifierApp(root)
    root.mainloop()
