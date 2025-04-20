import oss2
import os
import datetime
import uuid
from io import BytesIO
from PIL.PngImagePlugin import PngInfo
from comfy.cli_args import args
import ast

from .oss_utils import tensor_to_pil, image_to_base64, format_folder_path, generate_timestamp, OSS_ENDPOINT_LIST

class OSSAutoUploadNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prefix": ("STRING", {"default": "comfyui"}),
                "access_key_id": ("STRING", {"default": "access_key_id"}),
                "access_key_secret": ("STRING", {"default": "access_key_secret"}),
                "bucket_name": ("STRING", {"default": "bucket_name"}),
                "endpoint": (OSS_ENDPOINT_LIST, {"default": "oss-cn-hangzhou.aliyuncs.com"}),
                "folder": ("STRING", {"default": ""}),
            }
        }

    # 校验参数是否正确
    @classmethod
    def VALIDATE_INPUTS(cls, image, prefix, access_key_id, access_key_secret, bucket_name, endpoint, folder):
        print("参数校验:\t%s, %s, %s, %s, %s, %s" % (prefix, access_key_id, access_key_secret, bucket_name, endpoint, folder))
        if access_key_id == "" or access_key_secret == "" or bucket_name == "" or endpoint == "":
            return "关键参数不能为空"
        # 检查endpoint
        if endpoint not in OSS_ENDPOINT_LIST:
            return "endpoint 不正确\t %s" % endpoint
        return True
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("上传结果",)
    FUNCTION = "upload_to_oss"
    CATEGORY = "API/oss"
    OUTPUT_NODE = True
    
    def upload_to_oss(self, image, prefix, access_key_id, access_key_secret, bucket_name, endpoint, folder):
        print("参数信息: \t%s, %s, %s, %s, %s, %s\n" % (prefix, access_key_id, access_key_secret, bucket_name, endpoint, folder))
        
        results = []
        folder = format_folder_path(folder)
        
        for i, img in enumerate(image):
            # 自动生成文件名: 前缀_日期时间_uuid.jpg
            timestamp = generate_timestamp()
            unique_id = str(uuid.uuid4())[:8]  # 使用UUID的前8位
            
            filename = f"{folder}{prefix}_{timestamp}_{i}_{unique_id}.jpg"
            
            pil_img = tensor_to_pil(img)
            print(f"正在上传图片: {filename} \t文件类型: {type(pil_img)}")
            
            try:
                result = self.put_object(pil_img, filename, access_key_id, access_key_secret, bucket_name, endpoint)
                results.append(result)
            except Exception as e:
                error_msg = f"上传失败 {filename}: {str(e)}"
                print(error_msg)
                results.append(error_msg)

        return (", ".join(results),)

    def put_object(self, file, filename, access_key_id, access_key_secret, bucket_name, endpoint):
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)
        image_bytes = BytesIO()
        file.save(image_bytes, format='JPEG')  # 保存为 JPEG 格式
        image_bytes.seek(0)  # 将流指针回到开头
        try:
            bucket.put_object(filename, image_bytes)
            print(f'图片成功上传到 OSS，文件名为: {filename}')
            # 构建可能的URL（注意：这个URL可能需要根据你的OSS配置调整）
            url = f"https://{bucket_name}.{endpoint}/{filename}"
            return url
        except oss2.exceptions.OssError as e:
            raise ValueError(f'上传失败，错误信息: {e}')

# 节点映射字典
NODE_CLASS_MAPPINGS = {
    "OSSAutoUploadNode": OSSAutoUploadNode
}

# 节点显示名称映射字典
NODE_DISPLAY_NAME_MAPPINGS = {
    "OSSAutoUploadNode": "自动保存图片到OSS"
} 