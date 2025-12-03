from pathlib import Path
from openai import OpenAI
import numpy as np
import io
import torch

class TextToSpeech:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": ""}),
                "text": ("STRING", {"default": "", "multiline": True}),
                "voice": (["alloy", "echo", "fable", "onyx", "nova", "shimmer"],),
                "model": (["tts-1", "tts-1-hd"], {"default": "tts-1"}), # 添加模型选择
                "base_url": ("STRING", {"default": "https://www.agsvai.com/v1"}),
            }
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "text_to_speech"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def text_to_speech(self, api_key, text, voice, model, base_url):
        if not api_key or not text:
            print("TextToSpeech: api_key 或 text 不能为空")
            return (None,)
        try:
            try:
                import soundfile as sf
            except ImportError:
                print("TextToSpeech: 请先安装 soundfile: pip install soundfile[mp3]")
                return (None,)
            client = OpenAI(
                base_url=base_url,
                api_key=api_key
            )
            response = client.audio.speech.create(
                model=model,
                voice=voice,
                input=text
            )
            audio_bytes = response.content
            audio_buffer = io.BytesIO(audio_bytes)
            data, sample_rate = sf.read(audio_buffer)
            # data: shape (samples,) 或 (samples, channels)
            # 保证 data 形状为 (samples,) 或 (samples, channels)
            if data.ndim == 1:
                # 单通道，转为 (1, samples)
                data = np.expand_dims(data, axis=0)
            elif data.ndim == 2:
                # (samples, channels) -> (channels, samples)
                data = data.T
            else:
                print("TextToSpeech: 音频数据维度异常")
                return (None,)
            
            waveform = torch.from_numpy(data.astype(np.float32))
            
            # ComfyUI audio 格式要求: (batch, channels, samples)
            # 当前 waveform 是 (channels, samples)，需要增加 batch 维度
            waveform = waveform.unsqueeze(0)

            audio_dict = {"waveform": waveform, "sample_rate": sample_rate}
            return (audio_dict,)
        except Exception as e:
            print(f"TextToSpeech: 生成语音失败: {e}")
            return (None,)

NODE_CLASS_MAPPINGS = {
    "TextToSpeech": TextToSpeech,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextToSpeech": "文字转语音 TextToSpeech",
}
