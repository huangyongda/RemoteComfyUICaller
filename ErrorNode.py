class ErrorNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True}),
                "msg": ("STRING", {"default": "条件为 False，工作流终止。"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("msg",)
    FUNCTION = "run"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def run(self, condition, msg):
        if not condition:
            raise RuntimeError(msg)
        return (msg,)

NODE_CLASS_MAPPINGS = {
    "ErrorNode": ErrorNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ErrorNode": "报错节点 ErrorNode",
}
