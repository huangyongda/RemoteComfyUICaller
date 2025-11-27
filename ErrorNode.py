class ErrorNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True}),
                "string_value": ("STRING", {"default": ""}),
                "int_value": ("INT", {"default": 0}),
                "float_value": ("FLOAT", {"default": 0.0}),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "FLOAT")
    RETURN_NAMES = ("string_value", "int_value", "float_value")
    FUNCTION = "run"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def run(self, condition, string_value, int_value, float_value):
        if not condition:
            raise RuntimeError("ErrorNode: 条件为 False，工作流终止。")
        return (string_value, int_value, float_value)

NODE_CLASS_MAPPINGS = {
    "ErrorNode": ErrorNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ErrorNode": "报错节点 ErrorNode",
}
