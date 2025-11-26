import os
import glob
import random
from PIL import Image
import numpy as np
import torch

class LoadImgDir:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dir_path": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "seed": ("INT", {"default": 0}),
            }
        }

    # 返回：单张 IMAGE（用于预览）、所有 IMAGES（列表）、首张图片路径（STRING）
    RETURN_TYPES = ("IMAGE","IMAGE", "IMAGES", "STRING")
    RETURN_NAMES = ("image1","image2", "images", "first_image_path")
    FUNCTION = "load_img_dir"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def load_img_dir(self, dir_path, seed=0):
        """
        从指定文件夹加载所有图片并返回图片列表和第一张图片的路径。
        返回 (image, images_list, first_image_path)
        images_list: numpy.ndarray 列表（H,W,3 uint8）
        first_image_path: 字符串（首张图片的完整路径），若无图片则为空字符串
        """
        if not dir_path:
            print("LoadImgDir: 未提供文件夹路径")
            return (None, None, [], "")

        if not os.path.isdir(dir_path):
            print(f"LoadImgDir: 路径不存在或不是文件夹: {dir_path}")
            return (None, None, [], "")

        # 支持的图片扩展名（不区分大小写）
        exts = ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp", "*.tiff", "*.gif")
        files = []
        for ext in exts:
            files.extend(glob.glob(os.path.join(dir_path, ext)))
            files.extend(glob.glob(os.path.join(dir_path, ext.upper())))

        # 去重并排序
        files = sorted(list(dict.fromkeys(files)))
        files = sorted(dict.fromkeys(files), key=os.path.basename)

        if not files:
            print(f"LoadImgDir: 文件夹中未找到图片: {dir_path}")
            empty_tensor = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
            return (empty_tensor, empty_tensor, [], "")


        images = []
        first_path = files[0] if files else ""

        for fp in files:
            try:
                img = Image.open(fp).convert("RGB")
                arr = np.array(img, dtype=np.uint8)
                # 确保 arr 是 (H, W, 3)
                if arr.ndim == 2:  # 灰度图
                    arr = np.stack([arr]*3, axis=-1)
                elif arr.shape[2] == 4:  # RGBA
                    arr = arr[..., :3]
                arr = arr.astype(np.float32) / 255.0  # 0~1 float32
                tensor = torch.from_numpy(arr).unsqueeze(0)  # (1, H, W, 3)
                images.append(tensor)
            except Exception as e:
                print(f"LoadImgDir: 无法打开图片 {fp}: {e}")

        print(f"LoadImgDir: 加载图片数量 = {len(images)}, 首张 = {first_path}")
        first_image = images[0] if images else None
        send_image = images[1] if len(images) > 1 else None
        return (first_image, send_image, images, first_path)
    
    # Register the node
NODE_CLASS_MAPPINGS = {
    "LoadImgDir": LoadImgDir,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImgDir": "加载图片文件夹",
}