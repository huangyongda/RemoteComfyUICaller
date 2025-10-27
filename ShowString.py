print("✅ Loaded ShowString")

class ShowString:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
            },
            "optional": {
                "title": ("STRING", {"default": "Text Output", "multiline": False}),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "show_string"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def show_string(self, text, title="Text Output"):
        """
        显示字符串内容在ComfyUI界面上
        """
        print(f"[{title}] {text}")
        
        # 返回UI显示数据
        return {"ui": {"text": [f"{title}: {text}"]}}

class ShowStringMultiline:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
            },
            "optional": {
                "title": ("STRING", {"default": "Multiline Text Output", "multiline": False}),
                "max_lines": ("INT", {"default": 20, "min": 1, "max": 100}),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "show_multiline_string"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def show_multiline_string(self, text, title="Multiline Text Output", max_lines=20):
        """
        显示多行字符串内容在ComfyUI界面上
        """
        print(f"[{title}]")
        lines = text.split('\n')
        
        # 限制显示行数
        display_lines = lines[:max_lines]
        display_text = '\n'.join(display_lines)
        
        if len(lines) > max_lines:
            display_text += f"\n... (省略了 {len(lines) - max_lines} 行)"
        
        # 在控制台也显示
        for i, line in enumerate(display_lines):
            print(f"  {i+1:3d}: {line}")
        
        if len(lines) > max_lines:
            print(f"  ... (省略了 {len(lines) - max_lines} 行)")
        
        # 返回UI显示数据
        return {"ui": {"text": [f"{title}:\n{display_text}"]}}

class StringFormatter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "template": ("STRING", {"multiline": True, "default": "Hello {name}!"}),
            },
            "optional": {
                "value1": ("STRING", {"default": "", "multiline": False}),
                "value2": ("STRING", {"default": "", "multiline": False}),
                "value3": ("STRING", {"default": "", "multiline": False}),
                "value4": ("STRING", {"default": "", "multiline": False}),
                "value5": ("STRING", {"default": "", "multiline": False}),
                "key1": ("STRING", {"default": "name", "multiline": False}),
                "key2": ("STRING", {"default": "value2", "multiline": False}),
                "key3": ("STRING", {"default": "value3", "multiline": False}),
                "key4": ("STRING", {"default": "value4", "multiline": False}),
                "key5": ("STRING", {"default": "value5", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("formatted_text",)
    FUNCTION = "format_string"
    CATEGORY = "utils"

    def format_string(self, template, value1="", value2="", value3="", value4="", value5="",
                     key1="name", key2="value2", key3="value3", key4="value4", key5="value5"):
        """
        格式化字符串模板
        Args:
            template: 字符串模板，使用 {key} 作为占位符
            value1-5: 要替换的值
            key1-5: 对应的键名
        Returns:
            格式化后的字符串
        """
        # 构建替换字典
        replacements = {}
        
        values = [value1, value2, value3, value4, value5]
        keys = [key1, key2, key3, key4, key5]
        
        for key, value in zip(keys, values):
            if key and key.strip():  # 只有当key不为空时才添加
                replacements[key] = value
        
        try:
            # 使用format方法进行字符串格式化
            formatted_text = template.format(**replacements)
            print(f"格式化成功: {formatted_text[:100]}...")
            return (formatted_text,)
        except KeyError as e:
            error_msg = f"格式化错误: 模板中的键 {e} 未找到对应的值"
            print(error_msg)
            return (error_msg,)
        except Exception as e:
            error_msg = f"格式化错误: {str(e)}"
            print(error_msg)
            return (error_msg,)

# 节点映射
NODE_CLASS_MAPPINGS = {
    "ShowString": ShowString,
    "ShowStringMultiline": ShowStringMultiline,
    "StringFormatter": StringFormatter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ShowString": "显示字符串",
    "ShowStringMultiline": "显示多行字符串",
    "StringFormatter": "字符串格式化器",
}
