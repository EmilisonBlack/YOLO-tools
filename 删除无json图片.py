# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# 文件名: {删除无JSON图片}.py
# 功能: {使用X-AnyLabeling软件进行数据标注后，将会在图片目录下产生对应的json文件，有些时候，我们需要删除无json对应的图片，平时或许用不到，等需要的时候就懂了}
# 作者: {Emilison_Black}
# 创建日期: {2025年1月20日}
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

"""使用前请修改文件夹路径↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓"""

import os
import shutil

# 请在这里设置图片和标签文件夹的路径
IMAGE_DIR = r'打标文件/images'  # 替换为你的图片文件夹路径
LABEL_DIR = r'打标文件/images'  # 替换为你的标签文件夹路径
TRASH_DIR = r'\软删除文件'  # 替换为你的回收站文件夹路径


def soft_delete_orphan_images(image_dir, label_dir, trash_dir):
    """
    将没有对应标签文件（.json）的图片文件移动到回收站文件夹。

    参数:
        image_dir (str): 图片目录路径。
        label_dir (str): 标签目录路径。
        trash_dir (str): 回收站目录路径。
    """
    # 创建回收站文件夹（如果不存在）
    if not os.path.exists(trash_dir):
        os.makedirs(trash_dir)

    # 获取图片文件列表（不带扩展名）
    image_files = set(os.path.splitext(f)[0] for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png', '.jpeg')))

    # 获取标签文件列表（不带扩展名）
    label_files = set(os.path.splitext(f)[0] for f in os.listdir(label_dir) if f.endswith('.json'))

    # 找出没有对应标签文件的图片文件
    orphan_images = image_files - label_files

    # 将这些图片文件移动到回收站文件夹
    for image in orphan_images:
        # 查找图片文件的实际扩展名（可能是 .jpg, .png, .jpeg 等）
        for ext in ['.jpg', '.png', '.jpeg']:
            image_path = os.path.join(image_dir, image + ext)
            if os.path.exists(image_path):
                trash_path = os.path.join(trash_dir, image + ext)
                shutil.move(image_path, trash_path)
                print(f'Moved {image_path} to {trash_path}')
                break  # 找到后跳出循环

    print(f"清理完成。移动了 {len(orphan_images)} 个无对应标签文件的图片文件到回收站。")


# 调用函数清理无对应标签文件的图片文件
if __name__ == "__main__":
    # 检查文件夹路径是否存在
    if not os.path.exists(IMAGE_DIR):
        print(f"错误：图片文件夹路径不存在 - {IMAGE_DIR}")
    elif not os.path.exists(LABEL_DIR):
        print(f"错误：标签文件夹路径不存在 - {LABEL_DIR}")
    else:
        soft_delete_orphan_images(IMAGE_DIR, LABEL_DIR, TRASH_DIR)