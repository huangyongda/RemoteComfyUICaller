# __init__.py
from .RemoteComfyUICaller import RemoteComfyUICaller 
from .video_merge_node import VideoMergeNode  # 假设你有这个类
from .AudioMerger import AudioMerger


# 必须定义这个字典！键是节点在 UI 中显示的名称，值是类
# Register the node
NODE_CLASS_MAPPINGS = {
    "RemoteComfyUICaller": RemoteComfyUICaller,
     "VideoMergeNode": VideoMergeNode,
    "AudioMerger": AudioMerger,
}

NODE_DISPLAY_NAME_MAPPINGS = {
     "VideoMergeNode": "VideoMergeNode 视频合并节点",
    "RemoteComfyUICaller": "Remote ComfyUI Caller ",
    "AudioMerger": "Audio Merger",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
