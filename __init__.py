# __init__.py
from .RemoteComfyUICaller import RemoteComfyUICaller 
from .video_merge_node import VideoMergeNode  # 假设你有这个类
from .LLMApiNode import LLMApiNode
from .ShowString import ShowString, ShowStringMultiline, StringFormatter


# 必须定义这个字典！键是节点在 UI 中显示的名称，值是类
# Register the node
NODE_CLASS_MAPPINGS = {
    "RemoteComfyUICaller": RemoteComfyUICaller,
     "VideoMergeNode": VideoMergeNode,
    "LLMApiNode": LLMApiNode,
    "ShowString": ShowString,
    "ShowStringMultiline": ShowStringMultiline,
    "StringFormatter": StringFormatter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
     "RemoteComfyUICaller": "Remote ComfyUI Caller ",
     "VideoMergeNode": "视频合并节点",
    "LLMApiNode": "LLM API调用",
    "ShowString": "显示字符串",
    "ShowStringMultiline": "显示多行字符串",
    "StringFormatter": "字符串格式化器",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
