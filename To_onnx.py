# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# 文件名: {To_onnx}.py
# 功能: {将.PT的YOLO模型转换至onnx模型}
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

from ultralytics import YOLO

# 加载训练好的模型
model = YOLO('runs/best_model/exp_dick6/weights/best.pt')

# 导出为 ONNX 格式
model.export(format='onnx', imgsz=640, simplify=True)