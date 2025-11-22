import requests
import json
import torch
import numpy as np
from PIL import Image
from io import BytesIO
import time

print("✅ Loaded RemoteComfyUIAsyncCaller")

class RemoteComfyUIAsyncCaller:
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

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_id", "remote_base_url")
    FUNCTION = "submit_remote_prompt"
    CATEGORY = "remote"

    def upload_image(self, base_url, image_tensor, image_name):
        """上传图片到远程ComfyUI"""
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
            'image': (image_name, img_buffer, 'image/png'),
            'overwrite': (None, 'true')
        }
        
        try:
            resp = requests.post(upload_url, files=files, timeout=30)
            resp.raise_for_status()
            return resp.json().get('name', image_name)
        except Exception as e:
            raise RuntimeError(f"Failed to upload {image_name}: {e}")

    def submit_remote_prompt(self, remote_base_url, image1=None, image2=None, workflow_json="", timeout_seconds=30,
                             replace1_key="", replace1_value="", replace2_key="", replace2_value="",
                             replace3_key="", replace3_value="", replace4_key="", replace4_value="",
                             replace5_key="", replace5_value=""):
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
            "client_id": "remote_async_caller_node"
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

        # Return immediately: caller can use RemoteComfyUIWait with prompt_id + remote_base_url
        return (prompt_id, base_url)