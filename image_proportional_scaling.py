import torch
import numpy as np
from PIL import Image
import comfy.utils
import folder_paths

class ImageProportionalScaling:
    """
    图像等比倍数缩放节点
    支持等比放大和缩小，具有独立开关控制
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "图像": ("IMAGE",),
                "缩放倍数": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.01,
                    "max": 8.0,
                    "step": 0.01,
                    "display": "number",
                    "tooltip": "设置图像的缩放倍数，支持0.01到8.0倍"
                }),
                "放大开关": (["禁用", "启用"], {
                    "default": "禁用",
                    "tooltip": "开启后执行放大操作，关闭后不执行放大"
                }),
                "缩小开关": (["禁用", "启用"], {
                    "default": "禁用",
                    "tooltip": "开启后执行缩小操作，关闭后不执行缩小"
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("图像", "宽度", "高度")
    FUNCTION = "scale_image"
    CATEGORY = "南光AI/图像缩放"
    
    def scale_image(self, 图像, 缩放倍数, 放大开关, 缩小开关):
        """
        执行图像等比缩放
        """
        # 验证输入
        if 图像 is None:
            raise ValueError("请输入图像")
        
        # 获取原始尺寸
        if len(图像.shape) == 4:
            batch_size, height, width, channels = 图像.shape
            img_tensor = 图像[0]
        else:
            img_tensor = 图像
            height, width = img_tensor.shape[:2]
        
        # 检查开关状态
        放大启用 = 放大开关 == "启用"
        缩小启用 = 缩小开关 == "启用"
        
        # 验证开关逻辑
        if 放大启用 and 缩小启用:
            raise ValueError("放大开关和缩小开关不能同时启用，请只选择一个")
        
        if not 放大启用 and not 缩小启用:
            raise ValueError("请至少启用一个缩放开关（放大开关或缩小开关）")
        
        # 根据开关确定实际缩放倍数
        actual_scale = 缩放倍数
        
        if 放大启用:
            # 放大模式：倍数小于1时按1倍处理
            if actual_scale < 1.0:
                actual_scale = 1.0
            scaling_type = "放大"
        else:
            # 缩小模式：倍数大于1时按1倍处理
            if actual_scale > 1.0:
                actual_scale = 1.0
            scaling_type = "缩小"
        
        # 计算新尺寸
        new_width = max(1, int(width * actual_scale))
        new_height = max(1, int(height * actual_scale))
        
        # 如果尺寸没有变化，直接返回原图
        if new_width == width and new_height == height:
            if len(图像.shape) == 4:
                return (图像, new_width, new_height)
            else:
                return (图像.unsqueeze(0), new_width, new_height)
        
        # 转换图像格式并进行缩放
        try:
            # 将tensor转换为PIL图像
            if isinstance(img_tensor, torch.Tensor):
                img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
            else:
                img_np = (img_tensor * 255).astype(np.uint8)
            
            # 确保是RGB格式
            if img_np.shape[-1] == 4:
                pil_img = Image.fromarray(img_np, mode='RGBA').convert('RGB')
            else:
                pil_img = Image.fromarray(img_np, mode='RGB')
            
            # 执行高质量缩放
            resized_img = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换回tensor
            resized_np = np.array(resized_img).astype(np.float32) / 255.0
            resized_tensor = torch.from_numpy(resized_np).unsqueeze(0)
            
            # 输出结果
            print(f"[图像等比缩放] {scaling_type}完成: {width}x{height} -> {new_width}x{new_height}")
            
            return (resized_tensor, new_width, new_height)
            
        except Exception as e:
            raise RuntimeError(f"图像缩放失败: {str(e)}")


# 节点映射
NODE_CLASS_MAPPINGS = {
    "Comfyui_Image_Proportional_Scaling": ImageProportionalScaling
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "Comfyui_Image_Proportional_Scaling": "图像等比倍数缩放"
}