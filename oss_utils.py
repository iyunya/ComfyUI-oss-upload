import numpy as np
import base64
import io
from PIL import Image
import datetime
import os

def tensor_to_pil(image):
    """
    将张量转换为PIL图像
    
    Args:
        image: 输入图像张量
        
    Returns:
        PIL.Image: 转换后的PIL图像
    """
    return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

def image_to_base64(pil_image, pnginfo=None):
    """
    将PIL图像转换为base64编码
    
    Args:
        pil_image: PIL图像对象
        pnginfo: PNG图像信息
        
    Returns:
        str: base64编码的图像字符串
    """
    # 创建一个BytesIO对象，用于临时存储图像数据
    image_data = io.BytesIO()
    # 将图像保存到BytesIO对象中，格式为PNG
    pil_image.save(image_data, format='PNG', pnginfo=pnginfo)
    # 将BytesIO对象的内容转换为字节串
    image_data_bytes = image_data.getvalue()
    # 将图像数据编码为Base64字符串
    encoded_image = "data:image/png;base64," + base64.b64encode(image_data_bytes).decode('utf-8')
    return encoded_image

def format_folder_path(folder):
    """
    格式化文件夹路径，确保以/结尾但不以/开头
    
    Args:
        folder: 原始文件夹路径
        
    Returns:
        str: 格式化后的文件夹路径
    """
    if folder and folder.strip():
        # 确保文件夹路径格式正确，不以/开头，但以/结尾
        folder = folder.strip().rstrip('/') + '/'
        if folder.startswith('/'):
            folder = folder[1:]
    else:
        folder = ""
    
    return folder

def generate_timestamp():
    """
    生成时间戳字符串
    
    Returns:
        str: 格式化的时间戳
    """
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def check_directory(check_dir):
    """
    检查目录是否存在，如果不存在则创建
    
    Args:
        check_dir: 要检查的目录路径
        
    Returns:
        str: 规范化后的路径
    """
    check_dir = os.path.normpath(check_dir)
    if not os.path.isdir(check_dir):
        os.makedirs(check_dir, exist_ok=True)
    return check_dir

# OSS端点列表
OSS_ENDPOINT_LIST = [
    "oss-cn-hangzhou.aliyuncs.com",
    "oss-cn-hangzhou-internal.aliyuncs.com",
    "oss-cn-shanghai.aliyuncs.com",
    "oss-cn-shanghai-internal.aliyuncs.com",
    "oss-cn-beijing.aliyuncs.com",
    "oss-cn-beijing-internal.aliyuncs.com",
    "oss-cn-shenzhen.aliyuncs.com",
    "oss-cn-shenzhen-internal.aliyuncs.com",
    "oss-cn-qingdao.aliyuncs.com",
    "oss-cn-qingdao-internal.aliyuncs.com",
    "oss-cn-zhangjiakou.aliyuncs.com",
    "oss-cn-zhangjiakou-internal.aliyuncs.com",
    "oss-cn-huhehaote.aliyuncs.com",
    "oss-cn-huhehaote-internal.aliyuncs.com",
    "oss-cn-chengdu.aliyuncs.com",
    "oss-cn-chengdu-internal.aliyuncs.com"
]

# 支持的图片格式
IMAGE_FORMATS = [
    "JPEG",
    "PNG",
    "WEBP"
] 