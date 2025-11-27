import os

class CountFile:
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

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("file_count",)
    FUNCTION = "count_files"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def count_files(self, dir_path, seed: int = 0):
        """
        统计指定文件夹下的文件数量（不递归子文件夹）。
        返回: 文件数量（int）
        """
        if not dir_path or not os.path.isdir(dir_path):
            print(f"CountFile: 路径不存在或不是文件夹: {dir_path}")
            return (0,)
        # 只统计文件，不统计文件夹
        files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        count = len(files)
        print(f"CountFile: {dir_path} 文件数量 = {count}")
        return (count,)

NODE_CLASS_MAPPINGS = {
    "CountFile": CountFile,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CountFile": "统计文件夹文件数量",
}
