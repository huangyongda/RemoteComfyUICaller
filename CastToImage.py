class CastToImage:
    """
    接受任意类型 (*)，声明返回 IMAGE，并直接透传值。
    用法：AnyOutput -> CastToImage -> PreviewImage
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "inp": ("*",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "run"
    CATEGORY = "Utility"

    def run(self, inp):
        # 注意：ComfyUI 的节点返回都要是 tuple
        # 如果上游传 None，仍然返回 None，这样下游可以检测并跳过
        return (inp,)


NODE_CLASS_MAPPINGS = {
    "CastToImage": CastToImage
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CastToImage": "Cast -> IMAGE"
}
