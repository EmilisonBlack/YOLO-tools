# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# 文件名: {删除空内容txt文件}.py
# 功能: {使用X-AnyLabeling等软件进行数据标注后，可能由于误操作，导致生成了一堆没有内容的txt标签文件。这时候运行程序，就可以删除多余的标签}
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

"""请在代码底部MAIN函数中修改标签路径和回收站路径！！！！！！！！！！！！！！！！！！！！！！！"""

import os
import shutil
from datetime import datetime


def is_file_empty(file_path):
    """检查文件是否为空（0字节或只有空白字符）"""
    # 检查文件大小是否为0
    if os.path.getsize(file_path) == 0:
        return True

    # 检查是否只包含空白字符
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        return len(content.strip()) == 0


def soft_delete_files(source_dir, recycle_bin):
    """执行软删除操作"""
    # 验证源目录
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"源目录不存在: {source_dir}")

    # 创建回收站目录（如果不存在）
    os.makedirs(recycle_bin, exist_ok=True)

    # 遍历目录中的.txt文件
    deleted_files = []
    for filename in os.listdir(source_dir):
        if filename.lower().endswith('.txt'):
            file_path = os.path.join(source_dir, filename)

            # 跳过目录
            if not os.path.isfile(file_path):
                continue

            # 检查文件是否为空
            if is_file_empty(file_path):
                # 生成唯一文件名防止覆盖
                base_name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = f"{base_name}_{timestamp}{ext}"
                dest_path = os.path.join(recycle_bin, new_name)

                # 执行移动操作
                try:
                    shutil.move(file_path, dest_path)
                    deleted_files.append((filename, new_name))
                except Exception as e:
                    print(f"移动文件 {filename} 失败: {str(e)}")

    return deleted_files


if __name__ == "__main__":
    # 用户配置区域
    SOURCE_DIRECTORY = "data/labels/train"  # 需要扫描的目录
    RECYCLE_BIN = "软删除文件"  # 软删除目录

    # 执行操作
    try:
        result = soft_delete_files(SOURCE_DIRECTORY, RECYCLE_BIN)

        # 输出结果
        print(f"扫描完成，共发现 {len(result)} 个空文件：")
        for original, new_name in result:
            print(f"原文件名: {original} → 回收站文件名: {new_name}")

        # 在回收站目录生成日志
        log_path = os.path.join(RECYCLE_BIN, "operation_log.txt")
        with open(log_path, 'a', encoding='utf-8') as log:
            log.write(f"{datetime.now()} 操作日志：\n")
            log.write("\n".join([f"{orig} → {new}" for orig, new in result]))
            log.write("\n\n")

    except Exception as e:
        print(f"程序运行出错: {str(e)}")
    finally:
        input("\n按回车键退出程序...")