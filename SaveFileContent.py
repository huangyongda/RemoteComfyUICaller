
import os
print("✅ Loaded SaveFileContent")

# 保存文件内容
class SaveFileContent:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"forceInput": True}),
                "content": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "append": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "save"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def save(self, file_path, content, append=False):
        """
        保存内容到指定文件路径，可选择追加或覆盖。
        """
        mode = "a" if append else "w"
        try:
            with open(file_path, mode, encoding="utf-8") as f:
                if append:
                    f.write("\n" + content)
                else:
                    f.write(content)
            msg = f"内容已{'追加' if append else '覆盖'}到: {file_path}"
            print(f"[SaveFileContent] {msg}")
        except Exception as e:
            msg = f"保存文件失败: {e}"
            print(f"[SaveFileContent] {msg}")
        return (msg,)

# Register the node
NODE_CLASS_MAPPINGS = {
    "SaveFileContent": SaveFileContent,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveFileContent": "保存文件内容",
}