import os
from PIL import Image
import numpy as np

print("✅ Loaded SaveImage")

class SaveImage:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"forceInput": True}),
                "image": ("IMAGE", {"forceInput": True}),
            },
            "optional": {
                "title": ("STRING", {"default": "Save Image", "multiline": False}),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "save"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def save(self, file_path, image, title="Save Image"):
        """
        保存图片到指定路径，并在ComfyUI界面显示结果。
        """
        msg = f"{title}: {file_path}"
        try:
            # 如果 image 是 numpy 数组，转换为 PIL Image
            if isinstance(image, np.ndarray):
                if image.dtype != np.uint8:
                    image = (image * 255).clip(0, 255).astype(np.uint8)
                if image.ndim == 3 and image.shape[2] == 1:
                    image = image.squeeze(axis=2)
                pil_img = Image.fromarray(image)
            elif isinstance(image, Image.Image):
                pil_img = image
            else:
                raise ValueError("Unsupported image type")
            pil_img.save(file_path)
            print(f"Image saved: {file_path}")
        except Exception as e:
            print(f"Error saving image {file_path}: {e}")
            msg += f"\nError: {e}"
        return {"ui": {"text": [msg]}}

NODE_CLASS_MAPPINGS = {
    "SaveImage": SaveImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImage": "保存图片到指定路径",
}
