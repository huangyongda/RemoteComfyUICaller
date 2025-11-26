
import os
print("✅ Loaded StringReplacer")


#字符串替换
class StringReplacer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "string": ("STRING", {"default": "", "multiline": False}),
                "old_substring": ("STRING", {"default": "", "multiline": False}),
                "new_substring": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("replaced_string",)
    FUNCTION = "replace"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def replace(self, string, old_substring, new_substring):
        """
        在给定字符串中替换子字符串，并在ComfyUI界面显示结果。
        """
        replaced_string = string.replace(old_substring, new_substring)
        print(f"[String Replacement] {replaced_string}")
        return (replaced_string,)

# Register the node
NODE_CLASS_MAPPINGS = {
    "StringReplacer": StringReplacer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StringReplacer": "字符串替换器",
}