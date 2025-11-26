print("✅ Loaded StringConcat")

class StringConcat:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string1": ("STRING", {"default": "", "multiline": True}),
                "string2": ("STRING", {"default": "", "multiline": True}),
                "joiner": ("STRING", {"default": ","}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "concat"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def concat(self, string1, string2, joiner):
        """
        合并两个字符串，中间插入连接字符串。
        """
        result = f"{string1}{joiner}{string2}"
        print(f"[StringConcat] 合并结果: {result}")
        return (result,)

NODE_CLASS_MAPPINGS = {
    "StringConcat": StringConcat,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StringConcat": "字符串合并",
}
