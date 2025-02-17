# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# 文件名: {分类高质量图片对应txt}.py
# 功能: {分隔出高低质量图片后，程序将对应的txt图片存入对应的文件夹，用户需要手动修改3个参数，分别是高质量文件夹，低质量文件夹和对应txt文件的地址。}
# 作者: {Emilison_Black}
# 创建日期: {2025年2月14日}
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

def classify_txt_files(high_quality_image_dir, low_quality_image_dir, unclassified_txt_dir):
    """
    将未分类的txt文件根据其对应的高质量或低质量图片进行分类。

    参数:
        high_quality_image_dir (str): 高质量图片文件夹路径。
        low_quality_image_dir (str): 低质量图片文件夹路径。
        unclassified_txt_dir (str): 未分类的txt文件夹路径。
    """
    # 创建高质量和低质量txt文件夹
    high_quality_txt_dir = os.path.join(high_quality_image_dir, 'high_quality_labels')
    low_quality_txt_dir = os.path.join(low_quality_image_dir, 'low_quality_labels')
    os.makedirs(high_quality_txt_dir, exist_ok=True)
    os.makedirs(low_quality_txt_dir, exist_ok=True)

    # 获取高质量和低质量图片的文件名（不带扩展名）
    high_quality_images = set(os.path.splitext(f)[0] for f in os.listdir(high_quality_image_dir) if f.endswith(('.jpg', '.png', '.jpeg')))
    low_quality_images = set(os.path.splitext(f)[0] for f in os.listdir(low_quality_image_dir) if f.endswith(('.jpg', '.png', '.jpeg')))

    # 遍历未分类的txt文件夹
    for txt_file in os.listdir(unclassified_txt_dir):
        if txt_file.endswith('.txt'):
            txt_file_name = os.path.splitext(txt_file)[0]
            txt_file_path = os.path.join(unclassified_txt_dir, txt_file)

            # 检查对应的图片是否在高质量图片文件夹中
            if txt_file_name in high_quality_images:
                shutil.move(txt_file_path, os.path.join(high_quality_txt_dir, txt_file))
                print(f'Moved {txt_file_path} to {high_quality_txt_dir}')
            # 检查对应的图片是否在低质量图片文件夹中
            elif txt_file_name in low_quality_images:
                shutil.move(txt_file_path, os.path.join(low_quality_txt_dir, txt_file))
                print(f'Moved {txt_file_path} to {low_quality_txt_dir}')
            else:
                print(f'No corresponding image found for {txt_file_path}, keeping it in the original folder.')

    print("分类完成。")

# 调用函数进行分类
if __name__ == "__main__":
    # 设置文件夹路径
    HIGH_QUALITY_IMAGE_DIR = r'打标文件/images/高质量图片'  # 替换为你的高质量图片文件夹路径
    LOW_QUALITY_IMAGE_DIR = r'打标文件/images/低质量图片'  # 替换为你的低质量图片文件夹路径
    UNCLASSIFIED_TXT_DIR = r'打标文件/labels'  # 替换为你的未分类txt文件夹路径

    # 检查文件夹路径是否存在
    if not os.path.exists(HIGH_QUALITY_IMAGE_DIR):
        print(f"错误：高质量图片文件夹路径不存在 - {HIGH_QUALITY_IMAGE_DIR}")
    elif not os.path.exists(LOW_QUALITY_IMAGE_DIR):
        print(f"错误：低质量图片文件夹路径不存在 - {LOW_QUALITY_IMAGE_DIR}")
    elif not os.path.exists(UNCLASSIFIED_TXT_DIR):
        print(f"错误：未分类txt文件夹路径不存在 - {UNCLASSIFIED_TXT_DIR}")
    else:
        classify_txt_files(HIGH_QUALITY_IMAGE_DIR, LOW_QUALITY_IMAGE_DIR, UNCLASSIFIED_TXT_DIR)
