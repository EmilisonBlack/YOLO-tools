# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# 文件名: {移除错误编号的TXT文件}.py
# 功能: {如果在训练时，labels文件夹中混入了不该存在的TXT文件，例如训练对象只有2个，但是由于其他原因，混入了3个对象的TXT文件，那么就运行本程序，把不适于这个训练
# 项目的TXT文件删除}
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
import shutil
import time
import tkinter as tk
from tkinter import filedialog, messagebox


def find_and_move_files(input_folder, unwanted_label):
    # 目标文件夹（在代码中固定）
    destination_folder = os.path.join(input_folder, "软删除文件")#路径修改为自己项目的回收站

    # 如果目标文件夹不存在，则创建
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(input_folder, filename)
            try:
                # 打开文件并读取内容
                with open(file_path, "r") as file:
                    lines = file.readlines()
                    for line in lines:
                        # 检查是否包含不希望的标签
                        if line.startswith(str(unwanted_label) + " "):
                            # 显式关闭文件句柄
                            file.close()
                            # 短暂延迟，确保文件句柄释放
                            time.sleep(0.1)
                            # 检查文件是否可写
                            if os.access(file_path, os.W_OK):
                                # 移动文件到目标文件夹
                                shutil.move(file_path, os.path.join(destination_folder, filename))
                            else:
                                messagebox.showerror("错误", f"文件 {filename} 不可写，可能被占用。")
                            break  # 如果找到不希望的标签，直接移动文件并跳出循环
            except PermissionError:
                messagebox.showerror("错误", f"无法读取文件 {filename}，文件可能被占用。")


def start_processing():
    # 获取输入文件夹和不希望的标签
    input_folder = entry_folder.get()
    unwanted_label = entry_label.get()

    if not input_folder:
        messagebox.showerror("错误", "请选择输入文件夹！")
        return
    if not unwanted_label:
        messagebox.showerror("错误", "请输入不希望的标签！")
        return

    try:
        unwanted_label = int(unwanted_label)  # 将标签转换为整数
        find_and_move_files(input_folder, unwanted_label)
        messagebox.showinfo("完成", "文件处理完成！")
    except ValueError:
        messagebox.showerror("错误", "标签必须是整数！")


# 创建GUI界面
root = tk.Tk()
root.title("YOLO标签文件处理工具")

# 输入文件夹选择
label_folder = tk.Label(root, text="输入文件夹:")
label_folder.grid(row=0, column=0, padx=10, pady=10)
entry_folder = tk.Entry(root, width=40)
entry_folder.grid(row=0, column=1, padx=10, pady=10)
button_browse = tk.Button(root, text="浏览", command=lambda: entry_folder.insert(0, filedialog.askdirectory()))
button_browse.grid(row=0, column=2, padx=10, pady=10)

# 不希望的标签输入
label_label = tk.Label(root, text="不希望的标签:")
label_label.grid(row=1, column=0, padx=10, pady=10)
entry_label = tk.Entry(root, width=40)
entry_label.grid(row=1, column=1, padx=10, pady=10)

# 开始处理按钮
button_start = tk.Button(root, text="开始处理", command=start_processing)
button_start.grid(row=2, column=1, padx=10, pady=20)

# 运行主循环
root.mainloop()
