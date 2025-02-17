# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# 文件名: {重命名数据集}.py
# 功能: {我们在导入训练数据时，可能会分好几批次导入，为了区别每一批次的数据，运行这个程序，可以把对应的jpg图片和txt图片都修改成  ？？？0001 的格式，同时保持
# 图片和TXT文件的一一对应关系，但是要注意，txt文件和jpg文件需要放在同一目录下。第一次使用时先备份数据！！！}
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
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from ttkthemes import ThemedTk


class ImageRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片重命名工具")
        self.root.geometry("700x250")

        # 主题设置
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # 布局
        self.label_folder = ttk.Label(root, text="选择文件夹:")
        self.label_folder.grid(row=0, column=0, padx=10, pady=10)

        self.button_browse = ttk.Button(root, text="浏览", command=self.browse_folder)
        self.button_browse.grid(row=0, column=1, padx=10, pady=10)

        self.label_prefix = ttk.Label(root, text="输入前缀:")
        self.label_prefix.grid(row=1, column=0, padx=30, pady=10)

        self.entry_prefix = ttk.Entry(root)
        self.entry_prefix.grid(row=1, column=1, padx=10, pady=10)

        self.button_rename_all = ttk.Button(root, text="命名所有图片", command=self.rename_all_images)
        self.button_rename_all.grid(row=2, column=0, columnspan=2, pady=10)

        self.button_rename_with_txt = ttk.Button(root, text="仅命名有TXT的图片", command=self.rename_images_with_txt)
        self.button_rename_with_txt.grid(row=3, column=0, columnspan=2, pady=10)

        self.label_status = ttk.Label(root, text="")
        self.label_status.grid(row=4, column=0, columnspan=2)

    def browse_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.label_status.config(text=f"已选择文件夹: {self.folder_path}")

    def rename_all_images(self):
        """重命名所有图片，无论是否有TXT文件"""
        self._rename_images(rename_all=True)

    def rename_images_with_txt(self):
        """仅重命名有TXT文件的图片"""
        self._rename_images(rename_all=False)

    def _rename_images(self, rename_all):
        """重命名逻辑的核心方法"""
        prefix = self.entry_prefix.get()
        if not prefix:
            messagebox.showwarning("警告", "请输入前缀")
            return

        if not hasattr(self, 'folder_path'):
            messagebox.showwarning("警告", "请先选择文件夹")
            return

        try:
            images = [f for f in os.listdir(self.folder_path) if
                      f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            images.sort()

            for i, image in enumerate(images, start=1):
                old_image_path = os.path.join(self.folder_path, image)
                new_image_name = f"{prefix}{i:04d}{os.path.splitext(image)[1]}"
                new_image_path = os.path.join(self.folder_path, new_image_name)

                # 检查是否存在对应的TXT文件
                txt_file = os.path.splitext(image)[0] + '.txt'
                old_txt_path = os.path.join(self.folder_path, txt_file)

                if rename_all or os.path.exists(old_txt_path):
                    # 重命名图片
                    os.rename(old_image_path, new_image_path)

                    # 如果有TXT文件，则重命名TXT文件
                    if os.path.exists(old_txt_path):
                        new_txt_name = f"{prefix}{i:04d}.txt"
                        new_txt_path = os.path.join(self.folder_path, new_txt_name)
                        os.rename(old_txt_path, new_txt_path)

            self.label_status.config(text="重命名完成！")
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {e}")


if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = ImageRenamerApp(root)
    root.mainloop()
