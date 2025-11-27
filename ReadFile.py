import os
print("✅ Loaded ReadFile")

class ReadFile:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"forceInput": True}),
                "seed": ("INT", {"default": 0}),
            },
            "optional": {
                "title": ("STRING", {"default": "File Read", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "read"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def read(self, file_path, seed=0, title="File Read"):
        """
        读取指定路径的文件内容，并在ComfyUI界面显示结果。
        """
        print(f"[{title}] {file_path} (seed={seed})")
        msg = ""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                msg = f.read()
            print(f"File read: {file_path}")
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            msg = f"Error: {e}"
        return (msg,)

NODE_CLASS_MAPPINGS = {
    "ReadFile": ReadFile,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ReadFile": "读取文件",
}
