import numpy as np
import base64
import io
from PIL import Image
import datetime
import os
import uuid

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

# 支持的视频格式（ComfyUI目前只支持MP4）
VIDEO_FORMATS = [
    "mp4"
]

def get_video_info(video_path):
    """
    获取视频文件信息
    
    Args:
        video_path: 视频文件路径
        
    Returns:
        dict: 包含视频信息的字典
    """
    if not os.path.exists(video_path):
        return {"error": "视频文件不存在"}
    
    try:
        file_size = os.path.getsize(video_path)
        file_size_mb = file_size / (1024 * 1024)
        
        # 获取文件扩展名
        _, ext = os.path.splitext(video_path)
        ext = ext.lower().lstrip('.')
        
        return {
            "file_size": file_size,
            "file_size_mb": round(file_size_mb, 2),
            "extension": ext,
            "is_valid": ext in [fmt.lower() for fmt in VIDEO_FORMATS]
        }
    except Exception as e:
        return {"error": f"获取视频信息失败: {str(e)}"}

def validate_video_file(video_path, max_size_mb=None):
    """
    验证视频文件
    
    Args:
        video_path: 视频文件路径
        max_size_mb: 最大文件大小限制(MB)，None表示不限制
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    if not video_path or not video_path.strip():
        return False, "视频路径不能为空"
    
    if not os.path.exists(video_path):
        return False, f"视频文件不存在: {video_path}"
    
    if not os.path.isfile(video_path):
        return False, f"路径不是文件: {video_path}"
    
    video_info = get_video_info(video_path)
    
    if "error" in video_info:
        return False, video_info["error"]
    
    if not video_info["is_valid"]:
        return False, f"不支持的视频格式: {video_info['extension']}"
    
    if max_size_mb and video_info["file_size_mb"] > max_size_mb:
        return False, f"视频文件过大: {video_info['file_size_mb']}MB > {max_size_mb}MB"
    
    return True, "视频文件验证通过"

def generate_video_filename(prefix="video", include_date=True, extension="mp4", custom_name=None):
    """
    生成视频文件名
    
    Args:
        prefix: 文件名前缀
        include_date: 是否包含日期时间
        extension: 文件扩展名
        custom_name: 自定义文件名
        
    Returns:
        str: 生成的文件名
    """
    if custom_name and custom_name.strip():
        filename = custom_name.strip()
        # 确保有正确的扩展名
        if not filename.lower().endswith(f'.{extension.lower()}'):
            filename = f"{filename}.{extension}"
        return filename
    
    # 自动生成文件名
    timestamp = ""
    if include_date:
        timestamp = generate_timestamp() + "_"
    
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{prefix}_{timestamp}{unique_id}.{extension}"
    
    return filename 