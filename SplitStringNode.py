class SplitString:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_string": ("STRING", {"default": ""}),
                "delimiter": ("STRING", {"default": ","}),
                "index": ("STRING", {"default": "1"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "split_and_pick"
    CATEGORY = "utils"

    def split_and_pick(self, input_string, delimiter, index):
        parts = input_string.split(delimiter)
        # index: 1-based, negative means from end
        try:
            idx = int(index.strip())
        except Exception:
            return ("",)
        if idx == 0 or abs(idx) > len(parts):
            return ("",)
        if idx > 0:
            pick = parts[idx - 1]
        else:
            pick = parts[idx]
        return (pick,)

NODE_CLASS_MAPPINGS = {
    "SplitString": SplitString,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "SplitString": "字符串分割 Split String (Pick Part)",
}
