# custom_nodes/comfyui_if_node/__init__.py

class IfString:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True}),
                "true_value": ("STRING", {"default": ""}),
                "false_value": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = "logic"

    def execute(self, condition, true_value, false_value):
        return (true_value if condition else false_value,)


class IfInt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True}),
                "true_value": ("INT", {"default": 0}),
                "false_value": ("INT", {"default": 0}),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"
    CATEGORY = "logic"

    def execute(self, condition, true_value, false_value):
        return (true_value if condition else false_value,)


class IfFloat:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True}),
                "true_value": ("FLOAT", {"default": 0.0}),
                "false_value": ("FLOAT", {"default": 0.0}),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "execute"
    CATEGORY = "logic"

    def execute(self, condition, true_value, false_value):
        return (true_value if condition else false_value,)


class IfImage:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True}),
                "true_value": ("IMAGE",),
                "false_value": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = "logic"

    def execute(self, condition, true_value, false_value):
        return (true_value if condition else false_value,)


class IfImages:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True}),
                "true_value": ("IMAGES",),
                "false_value": ("IMAGES",),
            }
        }

    RETURN_TYPES = ("IMAGES",)
    FUNCTION = "execute"
    CATEGORY = "logic"

    def execute(self, condition, true_value, false_value):
        return (true_value if condition else false_value,)


# 注册
NODE_CLASS_MAPPINGS = {
    "IfString": IfString,
    "IfInt": IfInt,
    "IfFloat": IfFloat,
    "IfImage": IfImage,
    "IfImages": IfImages,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "IfString": "If (String)",
    "IfInt": "If (Int)",
    "IfFloat": "If (Float)",
    "IfImage": "If (Image)",
    "IfImages": "If (Images)",
}