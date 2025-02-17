# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# 文件名: {删除无图片标签}.py
# 功能: {使用X-AnyLabeling等软件进行数据标注后，可能由于误操作，导致删除掉了图片，但是对应标签还存在的情况。这时候运行程序，就可以删除多余的标签}
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

import os
import shutil

# 请在这里设置图片和标签文件夹的路径
IMAGE_DIR = r'打标文件/images'  # 替换为你的图片文件夹路径
LABEL_DIR = r'打标文件/labels'  # 替换为你的标签文件夹路径
TRASH_DIR = r'I:\Huge_project\pycharm\YOLO-8.3.32\软删除文件'  # 替换为你的回收站文件夹路径


def soft_delete_orphan_labels(image_dir, label_dir, trash_dir):
    """
    将没有对应图片的标签文件移动到回收站文件夹。

    参数:
        image_dir (str): 图片目录路径。
        label_dir (str): 标签目录路径。
        trash_dir (str): 回收站目录路径。
    """
    # 创建回收站文件夹（如果不存在）
    if not os.path.exists(trash_dir):
        os.makedirs(trash_dir)

    # 获取图片和标签文件列表（不带扩展名）
    image_files = set(os.path.splitext(f)[0] for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png', '.jpeg')))
    label_files = set(os.path.splitext(f)[0] for f in os.listdir(label_dir) if f.endswith('.txt'))

    # 找出没有对应图片的标签文件
    orphan_labels = label_files - image_files

    # 将这些标签文件移动到回收站文件夹
    for label in orphan_labels:
        label_path = os.path.join(label_dir, label + '.txt')
        trash_path = os.path.join(trash_dir, label + '.txt')
        shutil.move(label_path, trash_path)
        print(f'Moved {label_path} to {trash_path}')

    print(f"清理完成。移动了 {len(orphan_labels)} 个无对应图片的标签文件到回收站。")


# 调用函数清理无对应图片的标签文件
if __name__ == "__main__":
    # 检查文件夹路径是否存在
    if not os.path.exists(IMAGE_DIR):
        print(f"错误：图片文件夹路径不存在 - {IMAGE_DIR}")
    elif not os.path.exists(LABEL_DIR):
        print(f"错误：标签文件夹路径不存在 - {LABEL_DIR}")
    else:
        soft_delete_orphan_labels(IMAGE_DIR, LABEL_DIR, TRASH_DIR)