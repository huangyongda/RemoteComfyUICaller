
import os
print("✅ Loaded DeleteFile")


class DeleteFile:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"forceInput": True}),
            },
            "optional": {
                "title": ("STRING", {"default": "File Deletion", "multiline": False}),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "delete"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def delete(self, file_path, title="File Deletion"):
        """
        删除指定路径的文件，并在ComfyUI界面显示结果。
        """
        print(f"[{title}] {file_path}")
        msg = f"{title}: {file_path}"
        try:
            os.remove(file_path)
            print(f"File deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            msg += f"\nError: {e}"
        return {"ui": {"text": [msg]}}
    
    # Register the node
NODE_CLASS_MAPPINGS = {
    "DeleteFile": DeleteFile,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DeleteFile": "删除文件",
}