# __init__.py
from .RemoteComfyUICaller import RemoteComfyUICaller 
from .video_merge_node import VideoMergeNode  # 假设你有这个类
from .LLMApiNode import LLMApiNode
from .ShowString import ShowString, ShowStringMultiline, StringFormatter
from .JsonExtractorNode import JsonExtractorNode
from .RemoteComfyUIAsyncCaller import RemoteComfyUIAsyncCaller
from .RemoteComfyUIWait import RemoteComfyUIWait
from .RandomCacheBuster import RandomCacheBuster
from .LoadImgDir import LoadImgDir


# 必须定义这个字典！键是节点在 UI 中显示的名称，值是类
# Register the node
NODE_CLASS_MAPPINGS = {
    "RemoteComfyUICaller": RemoteComfyUICaller,
    "RemoteComfyUIAsyncCaller": RemoteComfyUIAsyncCaller,
    "RemoteComfyUIWait": RemoteComfyUIWait,
    "RandomCacheBuster": RandomCacheBuster,
    "LoadImgDir": LoadImgDir,
    "VideoMergeNode": VideoMergeNode,
    "LLMApiNode": LLMApiNode,
    "ShowString": ShowString,
    "ShowStringMultiline": ShowStringMultiline,
    "StringFormatter": StringFormatter,
    "JsonExtractorNode": JsonExtractorNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
     "RemoteComfyUICaller": "Remote ComfyUI Caller ",
     "RemoteComfyUIAsyncCaller": "远程 ComfyUI 异步调用器",
     "RemoteComfyUIWait": "远程 ComfyUI 等待器",
     "RandomCacheBuster": "随机缓存破坏器",
     "LoadImgDir": "加载图片文件夹",
     "VideoMergeNode": "视频合并节点",
    "LLMApiNode": "LLM API调用",
    "ShowString": "显示字符串",
    "ShowStringMultiline": "显示多行字符串",
    "StringFormatter": "字符串格式化器",
    "JsonExtractorNode": "JSON提取器",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
