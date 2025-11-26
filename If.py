class IFAnyType:
    """
    IF node with automatic type inference.
    It returns the SAME type as the connected true_value or false_value.
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "condition": ("FLOAT", {"default": 1.0}),
                "true_value": ("*",),
                "false_value": ("*",),
            }
        }

    # This enables dynamic type propagation
    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("output",)
    FUNCTION = "run"
    CATEGORY = "Logic/Advanced"

    # The magic: tell ComfyUI this output matches the input type
    @classmethod
    def VALIDATE_INPUTS(s, condition, true_value, false_value):
        # Determine type by inspecting connected input
        # true_value or false_value whichever is connected
        if true_value is not None:
            return (true_value,)
        if false_value is not None:
            return (false_value,)
        return None

    def run(self, condition, true_value, false_value):
        if float(condition) > 0:
            return (true_value,)
        else:
            return (false_value,)


NODE_CLASS_MAPPINGS = {
    "IFAnyType": IFAnyType
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "IFAnyType": "IF (Auto Type)"
}
