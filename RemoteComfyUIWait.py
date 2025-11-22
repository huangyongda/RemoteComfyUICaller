import requests
import json
import torch
import numpy as np
from PIL import Image
from io import BytesIO
import time

# Import helpers from the original module to reuse video/audio extraction code
from .RemoteComfyUICaller import RemoteComfyUICaller

print("✅ Loaded RemoteComfyUIWait")

class RemoteComfyUIWait:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "remote_base_url": ("STRING", {"default": "http://127.0.0.1:8087"}),
                "prompt_id": ("STRING", {"multiline": False}),
                "timeout_seconds": ("INT", {"default": 60, "min": 1, "max": 36000}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "AUDIO", "STRING", "STRING")
    RETURN_NAMES = ("image1", "image2", "video_frames", "audio", "prompt_id", "test_str")
    FUNCTION = "wait_for_remote_prompt"
    CATEGORY = "remote"

    def __init__(self):
        # helper instance to reuse existing video/audio helpers
        self.helper = RemoteComfyUICaller()

    def wait_for_remote_prompt(self, remote_base_url, prompt_id="", timeout_seconds=60):
        base_url = remote_base_url.rstrip('/')
        history_url = f"{base_url}/history/{prompt_id}"

        start_time = time.time()
        outputs = None
        while time.time() - start_time < timeout_seconds:
            time.sleep(1)
            try:
                hist_resp = requests.get(history_url, timeout=5)
                if hist_resp.status_code != 200:
                    continue
                history = hist_resp.json()
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    break
            except Exception:
                continue
        else:
            raise TimeoutError(f"Remote job did not complete within {timeout_seconds} seconds")

        # find image and video outputs
        image_infos = []
        video_info = None

        for node_id, node_output in outputs.items():
            if "images" in node_output:
                for img_info in node_output["images"]:
                    filename = img_info.get("filename", "")
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
                        image_infos.append(img_info)
                    elif filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                        if video_info is None:
                            video_info = img_info
            if "gifs" in node_output and len(node_output["gifs"]) > 0 and video_info is None:
                video_info = node_output["gifs"][0]

        if len(image_infos) < 2:
            while len(image_infos) < 2:
                image_infos.append(None)

        image_tensors = []
        view_url = f"{base_url}/view"

        for i in range(2):
            if i < len(image_infos) and image_infos[i] is not None:
                image_info = image_infos[i]
                filename = image_info.get("filename", "")
                subfolder = image_info.get("subfolder", "")
                type_dir = image_info.get("type", "output")
                try:
                    img_resp = requests.get(
                        view_url,
                        params={"filename": filename, "subfolder": subfolder, "type": type_dir},
                        timeout=10
                    )
                    img_resp.raise_for_status()
                    if len(img_resp.content) == 0:
                        raise ValueError("Empty image content")
                    img_buffer = BytesIO(img_resp.content)
                    img_buffer.seek(0)
                    image = Image.open(img_buffer).convert("RGB")
                    image_np = np.array(image).astype(np.float32) / 255.0
                    image_tensor = torch.from_numpy(image_np)[None,]
                    image_tensors.append(image_tensor)
                except Exception:
                    # retry with type='temp' if initial fails
                    try:
                        img_resp = requests.get(
                            view_url,
                            params={"filename": filename, "subfolder": subfolder, "type": "temp"},
                            timeout=10
                        )
                        img_resp.raise_for_status()
                        img_buffer = BytesIO(img_resp.content)
                        img_buffer.seek(0)
                        image = Image.open(img_buffer).convert("RGB")
                        image_np = np.array(image).astype(np.float32) / 255.0
                        image_tensor = torch.from_numpy(image_np)[None,]
                        image_tensors.append(image_tensor)
                        continue
                    except Exception:
                        image_tensors.append(torch.zeros((1, 512, 512, 3), dtype=torch.float32))
            else:
                image_tensors.append(torch.zeros((1, 512, 512, 3), dtype=torch.float32))

        # handle video + audio
        video_tensor = None
        audio_output = None

        if video_info:
            video_filename = video_info.get("filename", "")
            video_subfolder = video_info.get("subfolder", "")
            video_type_dir = video_info.get("type", "output")
            try:
                video_resp = requests.get(
                    view_url,
                    params={"filename": video_filename, "subfolder": video_subfolder, "type": video_type_dir},
                    timeout=30
                )
                video_resp.raise_for_status()
                video_content = video_resp.content
                # use helper to convert to frames and extract audio
                video_tensor = self.helper.video_to_frames(video_content)
                audio_output = self.helper.extract_audio_from_video(video_content)
            except Exception:
                video_tensor = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
                audio_output = None
        else:
            video_tensor = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
            audio_output = None

        if audio_output is None:
            audio_output = {
                "waveform": torch.zeros((1, 1, 1), dtype=torch.float32),
                "sample_rate": 44100
            }

        return (image_tensors[0], image_tensors[1], video_tensor, audio_output, prompt_id, "Remote wait successful")
