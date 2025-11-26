import secrets
import time
from typing import Optional

print("✅ Loaded RandomCacheBuster")

class RandomCacheBuster:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "length": ("INT", {"default": 12, "min": 4, "max": 256}),
                "prefix": ("STRING", {"default": ""}),
                "use_timestamp": ("BOOLEAN", {"default": False}),
                # 新增：外部触发用的可变输入（把一个会变化的值连到这里即可破坏缓存）
                "refresh": ("FLOAT", {"default": 0.0}),
                # 新增：自动在每次运行时包含时间戳以强制刷新缓存
                "auto": ("BOOLEAN", {"default": False}),
                "seed": ("INT", {"default": 0}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("cache_buster",)
    FUNCTION = "generate"
    CATEGORY = "utils"

    def generate(self, length: int = 12, prefix: Optional[str] = "", use_timestamp: bool = False, refresh: float = 0.0, auto: bool = False, seed: int = 0):
        # 生成高熵随机字符串并按需要截断
        rand = secrets.token_urlsafe((length * 3) // 4 + 2)  # 生成略长一些再截断，保证字符集丰富
        rand = rand.replace("-", "").replace("_", "")  # 可选：移除不想要的符号
        rand = rand[:max(1, length)]
        
        parts = []
        if prefix:
            parts.append(str(prefix))
        parts.append(rand)

        # 如果用户显式要求包含时间戳，或启用了 auto，则加入时间戳以确保每次运行输出不同（破坏缓存）
        if use_timestamp or auto:
            parts.append(str(int(time.time() * 1000)))  # 毫秒级时间戳

        # 如果提供了外部 refresh 值（通常是会变化的数），也把它包含进来以破坏缓存
        if refresh is not None and refresh != 0.0:
            parts.append(str(refresh))

        result = "-".join(parts) if prefix or use_timestamp or auto or (refresh is not None and refresh != 0.0) else rand
        return (result,)

    # Register the node
NODE_CLASS_MAPPINGS = {
    "RandomCacheBuster": RandomCacheBuster,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomCacheBuster": "随机缓存破坏器",
}