import requests
import json
import torch
import numpy as np
from PIL import Image
from io import BytesIO
import time
import uuid

print("✅ Loaded RemoteComfyUICaller")

class RemoteComfyUICaller:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "remote_base_url": ("STRING", {"default": "http://127.0.0.1:8087"}),
                "workflow_json": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "timeout_seconds": ("INT", {"default": 60, "min": 10, "max": 36000}),
            },
            "optional": {
                "image1": ("IMAGE",),
                "image2": ("IMAGE",),
                "replace1_key": ("STRING", {"default": "{{placeholder1}}", "multiline": False}),
                "replace1_value": ("STRING", {"default": "", "multiline": False}),
                "replace2_key": ("STRING", {"default": "{{placeholder2}}", "multiline": False}),
                "replace2_value": ("STRING", {"default": "", "multiline": False}),
                "replace3_key": ("STRING", {"default": "{{placeholder3}}", "multiline": False}),
                "replace3_value": ("STRING", {"default": "", "multiline": False}),
                "replace4_key": ("STRING", {"default": "{{placeholder4}}", "multiline": False}),
                "replace4_value": ("STRING", {"default": "", "multiline": False}),
                "replace5_key": ("STRING", {"default": "{{placeholder5}}", "multiline": False}),
                "replace5_value": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "AUDIO", "STRING", "STRING")
    RETURN_NAMES = ("image1", "image2", "video_frames", "audio", "prompt_id","test_str")  # 更明确的命名
    FUNCTION = "call_remote_comfyui"
    CATEGORY = "remote"

    def upload_image(self, base_url, image_tensor, image_name):
        """上传图片到远程ComfyUI"""
        # 为图片名添加随机hash和时间戳，避免同名覆盖
        ts = int(time.time() * 1000)
        rand_hash = uuid.uuid4().hex[:8]
        if '.' in image_name:
            name, ext = image_name.rsplit('.', 1)
            unique_image_name = f"{name}_{rand_hash}_{ts}.{ext}"
        else:
            unique_image_name = f"{image_name}_{rand_hash}_{ts}"

        # 转换tensor到PIL图片
        image_np = image_tensor.squeeze().cpu().numpy()  # [H, W, C]
        if image_np.max() <= 1.0:
            image_np = (image_np * 255).astype(np.uint8)
        
        pil_image = Image.fromarray(image_np)
        
        # 保存到字节流
        img_buffer = BytesIO()
        pil_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # 上传文件
        upload_url = f"{base_url}/upload/image"
        files = {
            'image': (unique_image_name, img_buffer, 'image/png'),
            'overwrite': (None, 'true')
        }
        
        try:
            resp = requests.post(upload_url, files=files, timeout=30)
            resp.raise_for_status()
            return resp.json().get('name', unique_image_name)
        except Exception as e:
            raise RuntimeError(f"Failed to upload {unique_image_name}: {e}")

    def extract_audio_from_video(self, video_content):
        """从视频中提取音频"""
        try:
            import tempfile
            import os
            
            # 保存临时视频文件
            temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            temp_video.write(video_content)
            temp_video.close()
            
            # 首先获取原始音频信息
            import subprocess
            probe_cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                '-show_streams', temp_video.name
            ]
            
            try:
                probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
                probe_data = json.loads(probe_result.stdout)
                
                # 查找音频流
                audio_stream = None
                for stream in probe_data.get('streams', []):
                    if stream.get('codec_type') == 'audio':
                        audio_stream = stream
                        break
                
                if audio_stream:
                    original_sample_rate = int(audio_stream.get('sample_rate', 44100))
                    original_channels = int(audio_stream.get('channels', 2))
                    print(f"Original audio: {original_sample_rate}Hz, {original_channels} channels")
                else:
                    original_sample_rate = 44100
                    original_channels = 2
                    print("No audio stream found, using defaults")
                    
            except Exception as e:
                print(f"Failed to probe audio info: {e}")
                original_sample_rate = 44100
                original_channels = 2
            
            # 使用ffmpeg提取音频，保持原始参数
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_audio.close()
            
            cmd = [
                'ffmpeg', '-i', temp_video.name, 
                '-vn', '-acodec', 'pcm_s16le',
                '-ar', str(original_sample_rate),  # 保持原始采样率
                '-ac', str(original_channels),     # 保持原始声道数
                '-y', temp_audio.name
            ]
            
            try:
                result = subprocess.run(cmd, check=True, capture_output=True)
                print(f"FFmpeg extraction successful")
            except subprocess.CalledProcessError as e:
                print(f"FFmpeg failed: {e.stderr.decode() if e.stderr else 'Unknown error'}")
                os.unlink(temp_video.name)
                os.unlink(temp_audio.name)
                return None
            
            # 读取音频数据
            import wave
            with wave.open(temp_audio.name, 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()
                
                print(f"Extracted audio: {sample_rate}Hz, {channels} channels, {len(frames)} bytes")
                
                # 转换为numpy数组
                audio_data = np.frombuffer(frames, dtype=np.int16)
                if channels == 2:
                    audio_data = audio_data.reshape(-1, 2)
                elif channels == 1:
                    # 如果是单声道，保持一维
                    pass
                else:
                    # 多声道情况，只取前两个声道
                    audio_data = audio_data.reshape(-1, channels)[:, :2]
                    if audio_data.shape[1] == 1:
                        audio_data = audio_data.squeeze()
                
                # 归一化到[-1, 1]，但保持动态范围
                audio_tensor = torch.from_numpy(audio_data.astype(np.float32) / 32767.0)
                
                # 确保tensor格式: [batch, channels, samples] 或 [batch, samples]
                if audio_tensor.dim() == 1:  # 单声道
                    audio_tensor = audio_tensor.unsqueeze(0)  # [1, samples]
                elif audio_tensor.dim() == 2:  # 立体声
                    audio_tensor = audio_tensor.transpose(0, 1).unsqueeze(0)  # [1, channels, samples]
                
            # 清理临时文件
            os.unlink(temp_video.name)
            os.unlink(temp_audio.name)
            
            return {"waveform": audio_tensor, "sample_rate": sample_rate}
            
        except Exception as e:
            print(f"Warning: Failed to extract audio from video: {e}")
            import traceback
            traceback.print_exc()
            return None

    def video_to_frames(self, video_content):
        """将视频内容转换为帧序列tensor"""
        try:
            import cv2
            import tempfile
            import os
            
            # 保存临时视频文件
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            temp_file.write(video_content)
            temp_file.close()
            
            # 使用OpenCV读取视频
            cap = cv2.VideoCapture(temp_file.name)
            frames = []
            
            # 获取视频尺寸
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"Video dimensions: {width}x{height}")
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # 确保frame不为空
                if frame is None:
                    break
                    
                # 转换BGR到RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 调试：检查帧数据
                print(f"Frame {frame_count}: shape={frame_rgb.shape}, min={frame_rgb.min()}, max={frame_rgb.max()}")
                
                # 转换为float32并归一化到[0,1]
                frame_np = frame_rgb.astype(np.float32) / 255.0
                frames.append(frame_np)
                
                frame_count += 1
                # 限制帧数防止内存溢出
                if frame_count >= 1000:
                    break
            
            cap.release()
            os.unlink(temp_file.name)  # 删除临时文件
            
            print(f"Extracted {len(frames)} frames")
            
            if frames:
                # 转换为tensor [frame_count, H, W, C] - 保持原始尺寸
                frames_array = np.stack(frames, axis=0)
                print(f"Stacked frames shape: {frames_array.shape}")
                video_tensor = torch.from_numpy(frames_array)
                
                # 确保tensor格式正确
                if video_tensor.dim() == 4:  # [N, H, W, C]
                    print(f"Video tensor shape: {video_tensor.shape}, dtype: {video_tensor.dtype}")
                    return video_tensor
                else:
                    print(f"Warning: Unexpected tensor dimensions: {video_tensor.shape}")
                    return torch.zeros((1, 512, 512, 3), dtype=torch.float32)
            else:
                # 返回空的视频tensor - 使用默认尺寸
                return torch.zeros((1, 512, 512, 3), dtype=torch.float32)
                
        except Exception as e:
            print(f"Warning: Failed to convert video to frames: {e}")
            return torch.zeros((1, 512, 512, 3), dtype=torch.float32)

    def call_remote_comfyui(self, remote_base_url, image1=None, image2=None, workflow_json="", timeout_seconds=30,
                           replace1_key="", replace1_value="", replace2_key="", replace2_value="",
                           replace3_key="", replace3_value="", replace4_key="", replace4_value="",
                           replace5_key="", replace5_value=""):
        print("call_remote_comfyui run >>>>>>>")
        base_url = remote_base_url.rstrip('/')
        prompt_url = f"{base_url}/prompt"

        # Step 1: 上传两张图片到远程服务器
        if image1 is not None:
            uploaded_image1 = self.upload_image(base_url, image1, "input_image1.png")
        else:
            uploaded_image1 = ""

        if image2 is not None:
            uploaded_image2 = self.upload_image(base_url, image2, "input_image2.png")
        else:
            uploaded_image2 = ""  # 若未提供 image2，则用空字符串替换占位符

        
        # 替换图片引用
        workflow_json = workflow_json.replace("{{image1}}", uploaded_image1)
        workflow_json = workflow_json.replace("{{image2}}", uploaded_image2)
        
        
        #如果replace1_value 有换行符，则需要转义
        replace1_value = replace1_value.replace("\n", "\\n")
        replace2_value = replace2_value.replace("\n", "\\n")
        replace3_value = replace3_value.replace("\n", "\\n")
        replace4_value = replace4_value.replace("\n", "\\n")
        replace5_value = replace5_value.replace("\n", "\\n")
        # " 也要转义
        replace1_value = replace1_value.replace('"', '\\"')
        replace2_value = replace2_value.replace('"', '\\"')
        replace3_value = replace3_value.replace('"', '\\"')
        replace4_value = replace4_value.replace('"', '\\"')
        replace5_value = replace5_value.replace('"', '\\"')

        #如果 replace1_value 的值等于seed:random，则生成一个随机数替换
        replace1_value = replace1_value.replace("seed:random", str(np.random.randint(0, 1000000)))
        replace2_value = replace2_value.replace("seed:random", str(np.random.randint(0, 1000000)))
        replace3_value = replace3_value.replace("seed:random", str(np.random.randint(0, 1000000)))
        replace4_value = replace4_value.replace("seed:random", str(np.random.randint(0, 1000000)))
        replace5_value = replace5_value.replace("seed:random", str(np.random.randint(0, 1000000)))
        


        # 执行5个自定义字符串替换
        replacements = [
            (replace1_key, replace1_value),
            (replace2_key, replace2_value),
            (replace3_key, replace3_value),
            (replace4_key, replace4_value),
            (replace5_key, replace5_value)
        ]
        
        for key, value in replacements:
            if key and key.strip():  # 只有当key不为空时才进行替换
                workflow_json = workflow_json.replace(key, value)
                print(f"Replaced '{key}' with '{value}'")

        # Step 2: 解析用户输入的原始工作流 JSON
        try:
            inner_prompt = json.loads(workflow_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid workflow JSON: {e}")

       

        # Step 4: 自动包裹成 ComfyUI API 要求的格式
        payload = {
            "prompt": inner_prompt,
            "client_id": "remote_caller_node"
        }

        # Step 5: 提交任务
        try:
            resp = requests.post(prompt_url, json=payload, timeout=10)
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to connect to remote ComfyUI ({prompt_url}): {e}")

        if resp.status_code != 200:
            raise RuntimeError(f"Submit failed: HTTP {resp.status_code} - {resp.text}")

        prompt_id = resp.json().get("prompt_id")
        if not prompt_id:
            raise RuntimeError("No prompt_id returned from remote server")

        # Step 6: 轮询历史，等待任务完成
        history_url = f"{base_url}/history/{prompt_id}"
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            time.sleep(1)
            try:
                hist_resp = requests.get(history_url, timeout=5)
                print(history_url)
                print(hist_resp)
                print(hist_resp.content)
                if hist_resp.status_code != 200:
                    continue
                history = hist_resp.json()
                # 调试：打印当前 history keys
                # print(f"[Remote Caller] History keys: {list(history.keys())}")
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    break
            except Exception:
                continue
        else:
            raise TimeoutError(f"Remote job did not complete within {timeout_seconds} seconds")

        # Step 7: 查找多个输出类型
        image_infos = []
        video_info = None
        
        for node_id, node_output in outputs.items():
            # 查找图片输出
            if "images" in node_output:
                for img_info in node_output["images"]:
                    # 检查文件扩展名，排除视频文件
                    filename = img_info["filename"]
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
                        image_infos.append(img_info)
                    elif filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                        # 视频文件也可能在images字段中
                        if video_info is None:
                            video_info = img_info
            
            # 查找视频输出 (VHS_VideoCombine或其他视频节点)
            if "gifs" in node_output and len(node_output["gifs"]) > 0:
                video_info = node_output["gifs"][0]  # 通常视频也存储在gifs字段中

        print(f"Found {len(image_infos)} images and {'1' if video_info else '0'} video")
        if video_info:
            print(f"Video info: {video_info}")

        # 处理图片输出
        if len(image_infos) < 2:
            # 如果图片不足2张，用空tensor填充
            empty_tensor = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
            while len(image_infos) < 2:
                image_infos.append(None)

        # Step 8: 下载并处理两张图片
        image_tensors = []
        view_url = f"{base_url}/view"
        
        for i in range(2):
            if i < len(image_infos) and image_infos[i] is not None:
                image_info = image_infos[i]
                filename = image_info["filename"]
                subfolder = image_info.get("subfolder", "")
                type_dir = image_info.get("type", "output")
                
                print(f"Downloading image {i+1}: filename={filename}, subfolder={subfolder}, type={type_dir}")
                
                try:
                    img_resp = requests.get(
                        view_url,
                        params={"filename": filename, "subfolder": subfolder, "type": type_dir},
                        timeout=10
                    )
                    img_resp.raise_for_status()
                    
                    print(f"Image {i+1} response: status={img_resp.status_code}, content_type={img_resp.headers.get('content-type')}, size={len(img_resp.content)}")
                    
                    # 检查响应内容是否为图片
                    if len(img_resp.content) == 0:
                        raise ValueError("Empty image content")
                    
                    # 检查content-type
                    content_type = img_resp.headers.get('content-type', '')
                    if not content_type.startswith('image/'):
                        print(f"Warning: Unexpected content-type: {content_type}")
                        print(f"Response content preview: {img_resp.content[:100]}")
                    
                    # 创建BytesIO对象并重置指针
                    img_buffer = BytesIO(img_resp.content)
                    img_buffer.seek(0)
                    
                    # 尝试打开图片
                    image = Image.open(img_buffer).convert("RGB")
                    image_np = np.array(image).astype(np.float32) / 255.0
                    image_tensor = torch.from_numpy(image_np)[None,]
                    image_tensors.append(image_tensor)
                    
                    print(f"Successfully processed image {i+1}: shape={image_tensor.shape}")
                    
                except Exception as e:
                    print(f"Warning: Failed to download image {i+1}: {e}")
                    print(f"Image info: {image_info}")
                    
                    # 尝试不同的文件类型参数
                    if type_dir == "output":
                        try:
                            print(f"Retrying with type='temp'...")
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
                            print(f"Successfully processed image {i+1} with type='temp'")
                            continue
                        except Exception as e2:
                            print(f"Retry with type='temp' also failed: {e2}")
                    
                    # 使用空tensor作为fallback
                    empty_tensor = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
                    image_tensors.append(empty_tensor)
            else:
                # 使用空tensor填充
                empty_tensor = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
                image_tensors.append(empty_tensor)

        # Step 9: 处理视频和音频输出
        video_tensor = None
        audio_output = None
        
        if video_info:
            video_filename = video_info["filename"]
            video_subfolder = video_info.get("subfolder", "")
            video_type_dir = video_info.get("type", "output")
            
            print(f"Downloading video: filename={video_filename}, subfolder={video_subfolder}, type={video_type_dir}")
            
            try:
                video_resp = requests.get(
                    view_url,
                    params={"filename": video_filename, "subfolder": video_subfolder, "type": video_type_dir},
                    timeout=30
                )
                video_resp.raise_for_status()
                
                print(f"Video response: status={video_resp.status_code}, content_type={video_resp.headers.get('content-type')}, size={len(video_resp.content)}")
                
                video_content = video_resp.content
                
                # 检查是否真的是视频文件
                content_type = video_resp.headers.get('content-type', '')
                if not content_type.startswith('video/') and not video_filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                    print(f"Warning: Expected video but got content-type: {content_type}")
                
                # 将视频转换为帧序列tensor - 保持原始尺寸
                video_tensor = self.video_to_frames(video_content)
                
                # 提取音频
                audio_output = self.extract_audio_from_video(video_content)
                    
            except Exception as e:
                print(f"Warning: Failed to download video: {e}")
                video_tensor = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
                audio_output = None
        else:
            print("No video output found")
            video_tensor = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
            audio_output = None

        # 如果没有音频，创建空的音频输出
        if audio_output is None:
            audio_output = {
                "waveform": torch.zeros((1, 1, 1), dtype=torch.float32), 
                "sample_rate": 44100
            }

        return (image_tensors[0], image_tensors[1], video_tensor, audio_output, prompt_id, "Remote call successful")

# Register the node
NODE_CLASS_MAPPINGS = {
    "RemoteComfyUICaller": RemoteComfyUICaller,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RemoteComfyUICaller": "远程 ComfyUI 调用器",
}