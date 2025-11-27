# custom_nodes/comfyui_type_cast/__init__.py

class IntToString:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("INT", {"default": 0}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "convert"
    CATEGORY = "type_cast"

    def convert(self, value):
        return (str(value),)


class FloatToString:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("FLOAT", {"default": 0.0}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "convert"
    CATEGORY = "type_cast"

    def convert(self, value):
        return (str(value),)


class StringToInt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("STRING", {"default": "0"}),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "convert"
    CATEGORY = "type_cast"

    def convert(self, value):
        try:
            return (int(float(value.strip())),)  # 允许 "3.0" 转为 3
        except Exception as e:
            raise ValueError(f"Cannot convert string '{value}' to int: {e}")


class StringToFloat:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("STRING", {"default": "0.0"}),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "convert"
    CATEGORY = "type_cast"

    def convert(self, value):
        try:
            return (float(value.strip()),)
        except Exception as e:
            raise ValueError(f"Cannot convert string '{value}' to float: {e}")


class IntToFloat:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("INT", {"default": 0}),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "convert"
    CATEGORY = "type_cast"

    def convert(self, value):
        return (float(value),)


class FloatToInt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("FLOAT", {"default": 0.0}),
                "rounding": (["floor", "ceil", "round"], {"default": "round"}),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "convert"
    CATEGORY = "type_cast"

    def convert(self, value, rounding):
        import math
        if rounding == "floor":
            return (math.floor(value),)
        elif rounding == "ceil":
            return (math.ceil(value),)
        else:  # round
            return (int(round(value)),)


# 注册所有节点
NODE_CLASS_MAPPINGS = {
    "IntToString": IntToString,
    "FloatToString": FloatToString,
    "StringToInt": StringToInt,
    "StringToFloat": StringToFloat,
    "IntToFloat": IntToFloat,
    "FloatToInt": FloatToInt,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "IntToString": "类型转化 Int to String",
    "FloatToString": "类型转化 Float to String",
    "StringToInt": "类型转化 String to Int",
    "StringToFloat": "类型转化 String to Float",
    "IntToFloat": "类型转化 Int to Float",
    "FloatToInt": "类型转化 Float to Int",
}