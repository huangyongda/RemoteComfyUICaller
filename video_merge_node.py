import torch
import numpy as np
from typing import Optional, Tuple, List

class VideoMergeNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video1": ("IMAGE",),  # 改为IMAGE类型
            },
            "optional": {
                "video2": ("IMAGE",),  # 改为IMAGE类型
                "video3": ("IMAGE",),  # 改为IMAGE类型
                "video4": ("IMAGE",),  # 改为IMAGE类型
                "video5": ("IMAGE",),  # 改为IMAGE类型
            }
        }
    
    RETURN_TYPES = ("IMAGE",)  # 返回IMAGE类型
    RETURN_NAMES = ("merged_video",)
    FUNCTION = "merge_videos"
    CATEGORY = "video"
    
    def merge_videos(self, video1, video2=None, video3=None, video4=None, video5=None):
        """
        合并多个视频（IMAGE类型的帧序列）
        Args:
            video1: 第一个视频（必需）- IMAGE类型 [batch, height, width, channels]
            video2-video5: 可选的额外视频 - IMAGE类型
        Returns:
            合并后的视频 - IMAGE类型
        """
        videos_to_merge = [video1]
        
        # 添加非空的可选视频
        for video in [video2, video3, video4, video5]:
            if video is not None:
                videos_to_merge.append(video)
        
        if len(videos_to_merge) == 1:
            return (video1,)
        
        print(f"合并 {len(videos_to_merge)} 个视频")
        
        # 提取视频张量数据并验证格式
        video_tensors = []
        for i, video in enumerate(videos_to_merge):
            print(f"视频{i+1} - 类型: {type(video)}, 形状: {video.shape if isinstance(video, torch.Tensor) else 'N/A'}")
            
            if isinstance(video, torch.Tensor):
                # 确保是4维张量 [batch/frames, height, width, channels]
                if video.dim() == 4:
                    video_tensors.append(video)
                    print(f"视频{i+1} - 接受张量形状: {video.shape}")
                else:
                    raise ValueError(f"视频{i+1}张量维度错误: 期望4维，得到{video.dim()}维")
            else:
                raise ValueError(f"视频{i+1}不是张量类型: {type(video)}")
        
        # 确保所有视频具有相同的空间维度（除了帧数）
        target_shape = video_tensors[0].shape[1:]  # (height, width, channels)
        print(f"目标形状: {target_shape}")
        
        processed_videos = []
        for i, video_tensor in enumerate(video_tensors):
            current_shape = video_tensor.shape[1:]
            if current_shape != target_shape:
                print(f"调整视频{i+1}尺寸: {current_shape} -> {target_shape}")
                video_tensor = self._resize_video(video_tensor, target_shape)
            processed_videos.append(video_tensor)
            print(f"处理后视频{i+1}形状: {video_tensor.shape}")
        
        # 沿时间轴（第0维）连接视频帧
        merged_tensor = torch.cat(processed_videos, dim=0)
        print(f"合并后视频形状: {merged_tensor.shape}")
        
        return (merged_tensor,)
    
    def _resize_video(self, video, target_shape):
        """
        调整视频尺寸以匹配目标形状
        Args:
            video: [frames, height, width, channels]
            target_shape: (target_height, target_width, channels)
        """
        import torch.nn.functional as F
        
        target_h, target_w, target_c = target_shape
        
        # 确保通道数匹配
        if video.shape[3] != target_c:
            if video.shape[3] == 3 and target_c == 3:
                pass  # RGB to RGB, 无需转换
            elif video.shape[3] == 1 and target_c == 3:
                # 灰度转RGB
                video = video.repeat(1, 1, 1, 3)
            elif video.shape[3] == 3 and target_c == 1:
                # RGB转灰度
                video = video.mean(dim=3, keepdim=True)
            else:
                # 其他情况，裁剪或填充通道
                if video.shape[3] > target_c:
                    video = video[:, :, :, :target_c]
                else:
                    padding = target_c - video.shape[3]
                    video = torch.cat([video, torch.zeros(*video.shape[:3], padding, dtype=video.dtype, device=video.device)], dim=3)
        
        # 如果空间尺寸已经匹配，直接返回
        if video.shape[1] == target_h and video.shape[2] == target_w:
            return video
        
        # 重塑为 (frames, channels, height, width) 用于插值
        video_reshaped = video.permute(0, 3, 1, 2)
        
        # 使用双线性插值调整尺寸
        resized = F.interpolate(
            video_reshaped, 
            size=(target_h, target_w), 
            mode='bilinear', 
            align_corners=False
        )
        
        # 重塑回 (frames, height, width, channels)
        return resized.permute(0, 2, 3, 1)

# 节点映射
NODE_CLASS_MAPPINGS = {
    "VideoMergeNode": VideoMergeNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoMergeNode": "视频合并节点"
}
