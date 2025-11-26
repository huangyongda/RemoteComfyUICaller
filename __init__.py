# __init__.py
import os
import importlib
import glob
from pathlib import Path

# 获取当前目录路径
NODE_DIR = Path(__file__).parent

# 初始化合并字典
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# 自动加载所有 .py 文件（排除 __init__.py）
py_files = glob.glob(os.path.join(NODE_DIR, "[!_]*.py"))  # 跳过 _ 开头和 __init__

for py_file in py_files:
    module_name = os.path.splitext(os.path.basename(py_file))[0]
    full_module_name = f"{__name__}.{module_name}"

    try:
        # 动态导入模块
        module = importlib.import_module(full_module_name)

        # 尝试从模块中获取 NODE_CLASS_MAPPINGS
        if hasattr(module, "NODE_CLASS_MAPPINGS"):
            NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
        else:
            print(f"[ComfyUI-MyNodes] 警告: {module_name} 未定义 NODE_CLASS_MAPPINGS")

        # 尝试合并 NODE_DISPLAY_NAME_MAPPINGS（可选）
        if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS"):
            NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)

    except Exception as e:
        print(f"[ComfyUI-MyNodes] 错误: 无法加载 {module_name}: {e}")
        # 可选：raise e 以中断加载（用于调试）