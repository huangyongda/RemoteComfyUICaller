
class TypeAutoCast:
    """
    自动将任意类型输入转换为常见类型输出
    支持：string, int, float, bool, image, images, list, dict, none
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input": ("*",),
            }
        }

    RETURN_TYPES = (
        "STRING", "INT", "FLOAT", "BOOL",
        "IMAGE", "IMAGES",
        "LIST", "DICT", "NONE"
    )
    RETURN_NAMES = (
        "string", "int", "float", "bool",
        "image", "images",
        "list", "dict", "none"
    )
    FUNCTION = "run"
    CATEGORY = "Logic/Advanced"

    def run(self, input):
        # STRING
        string = str(input) if input is not None else None

        # INT
        try:
            int_val = int(input)
        except (ValueError, TypeError):
            int_val = None

        # FLOAT
        try:
            float_val = float(input)
        except (ValueError, TypeError):
            float_val = None

        # BOOL
        try:
            bool_val = bool(input)
        except Exception:
            bool_val = None

        # IMAGE（假设ComfyUI的图片类型为dict且有"pixels"键）
        image = input if isinstance(input, dict) and "pixels" in input else None

        # IMAGES（list且每项为图片dict）
        images = input if isinstance(input, list) and all(isinstance(i, dict) and "pixels" in i for i in input) else None

        # LIST
        list_val = input if isinstance(input, list) else None

        # DICT
        dict_val = input if isinstance(input, dict) else None

        # NONE
        none_val = input if input is None else None

        return (
            string, int_val, float_val, bool_val,
            image, images,
            list_val, dict_val, none_val
        )

NODE_CLASS_MAPPINGS = {
    "TypeAutoCast": TypeAutoCast
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TypeAutoCast": "类型自动转换"
}