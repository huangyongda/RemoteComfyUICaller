# custom_nodes/comfyui_compare_node/__init__.py

class CompareInt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "a": ("INT", {"default": 0}),
                "b": ("INT", {"default": 0}),
                "operation": (["==", "!=", "<", "<=", ">", ">="],),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "compare"
    CATEGORY = "logic"

    def compare(self, a, b, operation):
        if operation == "==":
            result = a == b
        elif operation == "!=":
            result = a != b
        elif operation == "<":
            result = a < b
        elif operation == "<=":
            result = a <= b
        elif operation == ">":
            result = a > b
        elif operation == ">=":
            result = a >= b
        else:
            raise ValueError(f"Unsupported operation: {operation}")
        return (result,)


# 同理，可以为 FLOAT 和 STRING 添加类似节点
class CompareFloat:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "a": ("FLOAT", {"default": 0.0}),
                "b": ("FLOAT", {"default": 0.0}),
                "operation": (["==", "!=", "<", "<=", ">", ">="],),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "compare"
    CATEGORY = "logic"

    def compare(self, a, b, operation):
        # 注意：浮点比较可能需要容差，但这里按简单逻辑处理
        if operation == "==":
            result = a == b
        elif operation == "!=":
            result = a != b
        elif operation == "<":
            result = a < b
        elif operation == "<=":
            result = a <= b
        elif operation == ">":
            result = a > b
        elif operation == ">=":
            result = a >= b
        else:
            raise ValueError(f"Unsupported operation: {operation}")
        return (result,)


class CompareString:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "a": ("STRING", {"default": ""}),
                "b": ("STRING", {"default": ""}),
                "operation": (["==", "!=","contains", "not contains"],),  # 新增包含相关操作
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "compare"
    CATEGORY = "logic"

    def compare(self, a, b, operation):
        if operation == "==":
            result = a == b
        elif operation == "!=":
            result = a != b
        elif operation == "contains":
            result = b in a
        elif operation == "not contains":
            result = b not in a
        else:
            raise ValueError(f"Unsupported operation for string: {operation}")
        return (result,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "CompareInt": CompareInt,
    "CompareFloat": CompareFloat,
    "CompareString": CompareString,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CompareInt": "比较 Compare (Int)",
    "CompareFloat": "比较 Compare (Float)",
    "CompareString": "比较 Compare (String)",
}