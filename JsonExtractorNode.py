import json
import re


class JsonExtractorNode:
    """
    JSON提取节点 - 从JSON字符串中使用路径表达式提取值
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_string": ("STRING", {"multiline": True, "default": "{}"}),
                "json_path": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "extract_json_value"
    CATEGORY = "text/json"

    def extract_json_value(self, json_string, json_path):
        try:
            # 解析JSON字符串
            data = json.loads(json_string)
            
            # 提取值
            result = self._extract_by_path(data, json_path)
            
            # 如果结果是字典或列表，转换为JSON字符串
            if isinstance(result, (dict, list)):
                return (json.dumps(result, ensure_ascii=False),)
            
            # 其他类型转换为字符串
            return (str(result),)
            
        except json.JSONDecodeError as e:
            return (f"JSON解析错误: {str(e)}",)
        except Exception as e:
            return (f"路径提取错误: {str(e)}",)
    
    def _extract_by_path(self, data, path):
        """
        根据路径提取值
        支持的路径格式：
        - key: 直接访问键
        - key.subkey: 嵌套对象访问
        - [0]: 数组索引访问
        - key[0]: 对象的数组属性访问
        - key.subkey[0].name: 混合访问
        """
        if not path:
            return data
        
        current = data
        
        # 分解路径
        parts = self._parse_path(path)
        
        for part in parts:
            if isinstance(part, int):
                # 数组索引
                if isinstance(current, list) and 0 <= part < len(current):
                    current = current[part]
                else:
                    raise ValueError(f"无效的数组索引: {part}")
            else:
                # 对象键
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    raise ValueError(f"未找到键: {part}")
        
        return current
    
    def _parse_path(self, path):
        """
        解析路径字符串为部件列表
        例: "data.items[1].name" -> ["data", "items", 1, "name"]
        """
        parts = []
        
        # 使用正则表达式分割路径
        tokens = re.findall(r'[^.\[\]]+|\[\d+\]', path)
        
        for token in tokens:
            if token.startswith('[') and token.endswith(']'):
                # 数组索引
                index = int(token[1:-1])
                parts.append(index)
            else:
                # 对象键
                parts.append(token)
        
        return parts

    # Register the node
NODE_CLASS_MAPPINGS = {
    "JsonExtractorNode": JsonExtractorNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "JsonExtractorNode": "JSON提取节点",
}