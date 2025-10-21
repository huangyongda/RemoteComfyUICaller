import torch
import numpy as np

print("✅ Loaded AudioMerger")

class AudioMerger:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio1": ("AUDIO",),
            },
            "optional": {
                "audio2": ("AUDIO",),
                "audio3": ("AUDIO",),
                "audio4": ("AUDIO",),
                "audio5": ("AUDIO",),
                "merge_mode": (["concatenate", "mix", "overlay"], {"default": "concatenate"}),
            }
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("merged_audio",)
    FUNCTION = "merge_audio"
    CATEGORY = "remote/audio"

    def resample_audio(self, waveform, original_sr, target_sr):
        """简单的音频重采样"""
        if original_sr == target_sr:
            return waveform
        
        # 使用线性插值进行重采样
        original_length = waveform.shape[-1]
        target_length = int(original_length * target_sr / original_sr)
        
        if waveform.dim() == 2:  # [channels, samples]
            resampled = torch.zeros(waveform.shape[0], target_length, dtype=waveform.dtype)
            for ch in range(waveform.shape[0]):
                indices = torch.linspace(0, original_length - 1, target_length)
                resampled[ch] = torch.nn.functional.interpolate(
                    waveform[ch:ch+1].unsqueeze(0), 
                    size=target_length, 
                    mode='linear', 
                    align_corners=True
                ).squeeze()
        elif waveform.dim() == 3:  # [batch, channels, samples]
            resampled = torch.zeros(waveform.shape[0], waveform.shape[1], target_length, dtype=waveform.dtype)
            for b in range(waveform.shape[0]):
                for ch in range(waveform.shape[1]):
                    indices = torch.linspace(0, original_length - 1, target_length)
                    resampled[b, ch] = torch.nn.functional.interpolate(
                        waveform[b, ch:ch+1].unsqueeze(0), 
                        size=target_length, 
                        mode='linear', 
                        align_corners=True
                    ).squeeze()
        else:  # [samples]
            indices = torch.linspace(0, original_length - 1, target_length)
            resampled = torch.nn.functional.interpolate(
                waveform.unsqueeze(0).unsqueeze(0), 
                size=target_length, 
                mode='linear', 
                align_corners=True
            ).squeeze()
            
        return resampled

    def normalize_audio_format(self, audio_list):
        """统一音频格式：采样率、声道数、tensor维度"""
        if not audio_list:
            return []
        
        # 找到最高的采样率作为目标采样率
        target_sr = max(audio["sample_rate"] for audio in audio_list)
        print(f"Target sample rate: {target_sr}")
        
        # 找到最大声道数
        max_channels = 1
        for audio in audio_list:
            waveform = audio["waveform"]
            if waveform.dim() == 3:  # [batch, channels, samples]
                max_channels = max(max_channels, waveform.shape[1])
            elif waveform.dim() == 2:  # [channels, samples] or [batch, samples]
                if waveform.shape[0] <= 8:  # 假设声道数不会超过8
                    max_channels = max(max_channels, waveform.shape[0])
        
        print(f"Target channels: {max_channels}")
        
        normalized_audios = []
        for i, audio in enumerate(audio_list):
            waveform = audio["waveform"]
            sample_rate = audio["sample_rate"]
            
            print(f"Audio {i+1}: shape={waveform.shape}, sr={sample_rate}")
            
            # 重采样到目标采样率
            if sample_rate != target_sr:
                waveform = self.resample_audio(waveform, sample_rate, target_sr)
                print(f"  Resampled to {target_sr}Hz: shape={waveform.shape}")
            
            # 统一tensor维度为 [batch, channels, samples]
            if waveform.dim() == 1:  # [samples]
                waveform = waveform.unsqueeze(0).unsqueeze(0)  # [1, 1, samples]
            elif waveform.dim() == 2:  # [channels, samples] or [batch, samples]
                if waveform.shape[0] <= 8:  # 假设这是 [channels, samples]
                    waveform = waveform.unsqueeze(0)  # [1, channels, samples]
                else:  # 假设这是 [batch, samples]
                    waveform = waveform.unsqueeze(1)  # [batch, 1, samples]
            
            # 调整声道数
            current_channels = waveform.shape[1]
            if current_channels < max_channels:
                # 复制最后一个声道来填充
                last_channel = waveform[:, -1:, :]  # [batch, 1, samples]
                padding = last_channel.repeat(1, max_channels - current_channels, 1)
                waveform = torch.cat([waveform, padding], dim=1)
            elif current_channels > max_channels:
                # 截取前max_channels个声道
                waveform = waveform[:, :max_channels, :]
            
            normalized_audios.append({
                "waveform": waveform,
                "sample_rate": target_sr
            })
            print(f"  Normalized: shape={waveform.shape}")
        
        return normalized_audios, target_sr

    def merge_audio(self, audio1, audio2=None, audio3=None, audio4=None, audio5=None, merge_mode="concatenate"):
        # 收集所有非空的音频输入
        audio_inputs = [audio1]
        for audio in [audio2, audio3, audio4, audio5]:
            if audio is not None:
                audio_inputs.append(audio)
        
        print(f"Merging {len(audio_inputs)} audio inputs with mode: {merge_mode}")
        
        # 统一音频格式
        normalized_audios, target_sr = self.normalize_audio_format(audio_inputs)
        
        if merge_mode == "concatenate":
            # 串联模式：将音频首尾相接
            waveforms = [audio["waveform"] for audio in normalized_audios]
            merged_waveform = torch.cat(waveforms, dim=2)  # 在samples维度上连接
            
        elif merge_mode == "mix":
            # 混合模式：将音频叠加并平均
            # 找到最长的音频长度
            max_length = max(audio["waveform"].shape[2] for audio in normalized_audios)
            
            # 将所有音频填充到相同长度
            padded_waveforms = []
            for audio in normalized_audios:
                waveform = audio["waveform"]
                if waveform.shape[2] < max_length:
                    padding = torch.zeros(waveform.shape[0], waveform.shape[1], 
                                        max_length - waveform.shape[2], dtype=waveform.dtype)
                    waveform = torch.cat([waveform, padding], dim=2)
                padded_waveforms.append(waveform)
            
            # 叠加并平均
            stacked = torch.stack(padded_waveforms, dim=0)  # [num_audios, batch, channels, samples]
            merged_waveform = torch.mean(stacked, dim=0)  # [batch, channels, samples]
            
        elif merge_mode == "overlay":
            # 叠加模式：简单相加（可能会导致音量过大）
            max_length = max(audio["waveform"].shape[2] for audio in normalized_audios)
            
            # 初始化结果
            batch_size = normalized_audios[0]["waveform"].shape[0]
            channels = normalized_audios[0]["waveform"].shape[1]
            merged_waveform = torch.zeros(batch_size, channels, max_length, 
                                        dtype=normalized_audios[0]["waveform"].dtype)
            
            # 逐个叠加
            for audio in normalized_audios:
                waveform = audio["waveform"]
                length = waveform.shape[2]
                merged_waveform[:, :, :length] += waveform
        
        # 限制幅度范围到[-1, 1]
        merged_waveform = torch.clamp(merged_waveform, -1.0, 1.0)
        
        print(f"Merged audio shape: {merged_waveform.shape}, sample_rate: {target_sr}")
        
        result_audio = {
            "waveform": merged_waveform,
            "sample_rate": target_sr
        }
        
        return (result_audio,)
