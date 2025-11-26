import random

print("✅ Loaded RandomLinePicker")

class RandomLinePicker:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "seed": ("INT", {"default": 0}),
                "lines_string": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("picked_line",)
    FUNCTION = "pick"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def pick(self, lines_string,seed:int=0):
        """
        从多行字符串中随机选取一行。
        """
        lines = [line for line in lines_string.splitlines() if line.strip()]
        picked_line = random.choice(lines) if lines else ""
        print(f"[Random Line Picker] {picked_line}")
        return (picked_line,)

NODE_CLASS_MAPPINGS = {
    "RandomLinePicker": RandomLinePicker,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomLinePicker": "随机行选择器",
}
