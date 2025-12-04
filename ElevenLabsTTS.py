import requests
import io
import torch
import numpy as np

class ElevenLabsTTS:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": ""}),
                "text": ("STRING", {"default": "", "multiline": True}),
                "voice_id": ("STRING", {"default": "hkfHEbBvdQFNX4uWHqRF"}), # 默认 
                "model_id": (["eleven_multilingual_v2", "eleven_turbo_v2_5", "eleven_turbo_v2", "eleven_monolingual_v1"], {"default": "eleven_multilingual_v2"}),
                "stability": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "similarity_boost": ("FLOAT", {"default": 0.75, "min": 0.0, "max": 1.0, "step": 0.05}),
            }
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "text_to_speech"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def text_to_speech(self, api_key, text, voice_id, model_id, stability, similarity_boost):
        if not api_key or not text:
            print("ElevenLabsTTS: api_key 或 text 不能为空")
            return (None,)
        
        try:
            import soundfile as sf
        except ImportError:
            print("ElevenLabsTTS: 请先安装 soundfile: pip install soundfile[mp3]")
            return (None,)

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code != 200:
                print(f"ElevenLabsTTS: API Error {response.status_code}: {response.text}")
                return (None,)

            audio_buffer = io.BytesIO(response.content)
            data, sample_rate = sf.read(audio_buffer)

            # data: shape (samples,) 或 (samples, channels)
            if data.ndim == 1:
                data = np.expand_dims(data, axis=0)
            elif data.ndim == 2:
                data = data.T
            else:
                print("ElevenLabsTTS: 音频数据维度异常")
                return (None,)
            
            waveform = torch.from_numpy(data.astype(np.float32))
            # ComfyUI audio 格式要求: (batch, channels, samples)
            waveform = waveform.unsqueeze(0)

            audio_dict = {"waveform": waveform, "sample_rate": sample_rate}
            return (audio_dict,)

        except Exception as e:
            print(f"ElevenLabsTTS: 生成语音失败: {e}")
            return (None,)

NODE_CLASS_MAPPINGS = {
    "ElevenLabsTTS": ElevenLabsTTS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ElevenLabsTTS": "ElevenLabs TextToSpeech 文本转语音",
}
