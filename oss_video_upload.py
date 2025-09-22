import oss2
import os
import datetime
import uuid
from io import BytesIO
import tempfile
import shutil
from comfy.cli_args import args

from .oss_utils import (
    format_folder_path, 
    generate_timestamp, 
    OSS_ENDPOINT_LIST
)

# ComfyUI视频上传节点 - 支持MP4格式

class OSSVideoUploadNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO",),  # 视频输入
                "prefix": ("STRING", {"default": "comfyui_video"}),
                "access_key_id": ("STRING", {"default": "access_key_id"}),
                "access_key_secret": ("STRING", {"default": "access_key_secret"}),
                "bucket_name": ("STRING", {"default": "bucket_name"}),
                "endpoint": (OSS_ENDPOINT_LIST, {"default": "oss-cn-hangzhou.aliyuncs.com"}),
                "folder": ("STRING", {"default": "video"}),
                "include_date": (["是", "否"], {"default": "是"}),
            },
            "optional": {
                "use_temporary_url": (["是", "否"], {"default": "否"}),
                "expiration_hours": ("INT", {"default": 24, "min": 1, "max": 720, "step": 1}),
                "custom_filename": ("STRING", {"default": ""}),
            }
        }

    # 校验参数是否正确
    @classmethod
    def VALIDATE_INPUTS(cls, video, prefix, access_key_id, access_key_secret, bucket_name, endpoint, folder, include_date, use_temporary_url=None, expiration_hours=None, custom_filename=None):
        print("视频上传参数校验:\t%s, %s, %s, %s, %s, %s, %s" % (prefix, access_key_id, access_key_secret, bucket_name, endpoint, folder, include_date))
        
        if access_key_id == "" or access_key_secret == "" or bucket_name == "" or endpoint == "":
            return "关键参数不能为空"
            
        # 检查endpoint
        if endpoint not in OSS_ENDPOINT_LIST:
            return "endpoint 不正确\t %s" % endpoint
            
        return True
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("上传结果",)
    FUNCTION = "upload_video_to_oss"
    CATEGORY = "API/oss"
    OUTPUT_NODE = True
    
    def upload_video_to_oss(self, video, prefix, access_key_id, access_key_secret, bucket_name, endpoint, folder, include_date, use_temporary_url="否", expiration_hours=24, custom_filename=""):
        print("视频上传参数信息: \t%s, %s, %s, %s, %s, %s, %s\n" % (prefix, access_key_id, access_key_secret, bucket_name, endpoint, folder, include_date))
        
        folder = format_folder_path(folder)
        
        try:
            # 生成文件名
            if custom_filename and custom_filename.strip():
                # 使用自定义文件名
                base_filename = custom_filename.strip()
                # 确保文件名有正确的扩展名
                if not base_filename.endswith('.mp4'):
                    base_filename = f"{base_filename}.mp4"
                filename = f"{folder}{base_filename}"
            else:
                # 自动生成文件名
                timestamp = ""
                if include_date == "是":
                    timestamp = generate_timestamp() + "_"
                
                unique_id = str(uuid.uuid4())[:8]  # 使用UUID的前8位
                filename = f"{folder}{prefix}_{timestamp}{unique_id}.mp4"
            
            print(f"正在上传视频: {filename}")
            
            result = self.put_video_object(video, filename, access_key_id, access_key_secret, bucket_name, endpoint, use_temporary_url, expiration_hours)
            return (result,)
            
        except Exception as e:
            error_msg = f"视频上传失败: {str(e)}"
            print(error_msg)
            return (error_msg,)

    def put_video_object(self, video, filename, access_key_id, access_key_secret, bucket_name, endpoint, use_temporary_url="否", expiration_hours=24):
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)
        
        try:
            # 将视频对象转换为字节流
            video_bytes = BytesIO()
            
            # 使用MP4格式（ComfyUI目前只支持MP4）
            from comfy_api.util import VideoContainer, VideoCodec
            
            # 保存视频到字节流
            video.save_to(video_bytes, format=VideoContainer.MP4, codec=VideoCodec.AUTO)
            video_bytes.seek(0)
            
            # 上传到OSS
            bucket.put_object(filename, video_bytes)
            
            print(f'视频成功上传到 OSS，文件名为: {filename}')
            
            if use_temporary_url == "是":
                # 生成带有过期时间的临时URL
                url = bucket.sign_url('GET', filename, expiration_hours * 3600)  # 转换为秒
                # 确保URL使用https协议
                if url.startswith('http://'):
                    url = 'https://' + url[7:]
                print(f'生成临时URL，过期时间: {expiration_hours}小时')
            else:
                # 构建普通URL
                url = f"https://{bucket_name}.{endpoint}/{filename}"
            
            return url
            
        except oss2.exceptions.OssError as e:
            raise ValueError(f'视频上传失败，错误信息: {e}')
        except Exception as e:
            raise ValueError(f'视频处理失败，错误信息: {e}')

class OSSVideoAdvancedUploadNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO",),  # 视频输入
                "prefix": ("STRING", {"default": "comfyui_video"}),
                "access_key_id": ("STRING", {"default": "access_key_id"}),
                "access_key_secret": ("STRING", {"default": "access_key_secret"}),
                "bucket_name": ("STRING", {"default": "bucket_name"}),
                "endpoint": (OSS_ENDPOINT_LIST, {"default": "oss-cn-hangzhou.aliyuncs.com"}),
                "folder": ("STRING", {"default": "video"}),
                "include_date": (["是", "否"], {"default": "是"}),
                "multipart_threshold": ("INT", {"default": 100, "min": 1, "max": 1000, "step": 1}),  # MB
            },
            "optional": {
                "use_temporary_url": (["是", "否"], {"default": "否"}),
                "expiration_hours": ("INT", {"default": 24, "min": 1, "max": 720, "step": 1}),
                "custom_filename": ("STRING", {"default": ""}),
                "content_type": ("STRING", {"default": "video/mp4"}),
            }
        }

    # 校验参数是否正确
    @classmethod
    def VALIDATE_INPUTS(cls, video, prefix, access_key_id, access_key_secret, bucket_name, endpoint, folder, include_date, multipart_threshold, use_temporary_url=None, expiration_hours=None, custom_filename=None, content_type=None):
        print("高级视频上传参数校验:\t%s, %s, %s, %s, %s, %s, %s, %s" % (prefix, access_key_id, access_key_secret, bucket_name, endpoint, folder, include_date, multipart_threshold))
        
        if access_key_id == "" or access_key_secret == "" or bucket_name == "" or endpoint == "":
            return "关键参数不能为空"
            
        # 检查endpoint
        if endpoint not in OSS_ENDPOINT_LIST:
            return "endpoint 不正确\t %s" % endpoint
            
        # 检查分片上传阈值
        if multipart_threshold < 1 or multipart_threshold > 1000:
            return "分片上传阈值范围应为1-1000MB"
            
        return True
    
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("上传结果", "文件大小", "上传时间(秒)")
    FUNCTION = "upload_video_to_oss_advanced"
    CATEGORY = "API/oss"
    OUTPUT_NODE = True
    
    def upload_video_to_oss_advanced(self, video, prefix, access_key_id, access_key_secret, bucket_name, endpoint, folder, include_date, multipart_threshold, use_temporary_url="否", expiration_hours=24, custom_filename="", content_type="video/mp4"):
        print("高级视频上传参数信息: \t%s, %s, %s, %s, %s, %s, %s, %s\n" % (prefix, access_key_id, access_key_secret, bucket_name, endpoint, folder, include_date, multipart_threshold))
        
        folder = format_folder_path(folder)
        
        try:
            # 生成文件名
            if custom_filename and custom_filename.strip():
                # 使用自定义文件名
                base_filename = custom_filename.strip()
                # 确保文件名有正确的扩展名
                if not base_filename.endswith('.mp4'):
                    base_filename = f"{base_filename}.mp4"
                filename = f"{folder}{base_filename}"
            else:
                # 自动生成文件名
                timestamp = ""
                if include_date == "是":
                    timestamp = generate_timestamp() + "_"
                
                unique_id = str(uuid.uuid4())[:8]  # 使用UUID的前8位
                filename = f"{folder}{prefix}_{timestamp}{unique_id}.mp4"
            
            print(f"正在上传视频: {filename}")
            
            start_time = datetime.datetime.now()
            result, file_size_mb = self.put_video_object_advanced(video, filename, access_key_id, access_key_secret, bucket_name, endpoint, multipart_threshold, use_temporary_url, expiration_hours, content_type)
            end_time = datetime.datetime.now()
            
            upload_time = int((end_time - start_time).total_seconds())
            
            return (result, f"{file_size_mb:.2f} MB", upload_time)
            
        except Exception as e:
            error_msg = f"视频上传失败: {str(e)}"
            print(error_msg)
            return (error_msg, "0 MB", 0)

    def put_video_object_advanced(self, video, filename, access_key_id, access_key_secret, bucket_name, endpoint, multipart_threshold, use_temporary_url="否", expiration_hours=24, content_type="video/mp4"):
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)
        
        try:
            # 将视频对象转换为字节流
            video_bytes = BytesIO()
            
            # 使用MP4格式（ComfyUI目前只支持MP4）
            from comfy_api.util import VideoContainer, VideoCodec
            
            # 保存视频到字节流
            video.save_to(video_bytes, format=VideoContainer.MP4, codec=VideoCodec.AUTO)
            video_bytes.seek(0)
            
            # 获取文件大小
            file_size = len(video_bytes.getvalue())
            file_size_mb = file_size / (1024*1024)
            
            print(f"视频文件大小: {file_size_mb:.2f} MB")
            
            # 设置Content-Type
            headers = {'Content-Type': content_type}
            
            if file_size_mb > multipart_threshold:
                # 使用分片上传
                print(f"文件大小 {file_size_mb:.2f}MB 超过阈值 {multipart_threshold}MB，使用分片上传")
                
                # 初始化分片上传
                upload_id = bucket.init_multipart_upload(filename, headers=headers).upload_id
                
                # 分片大小设为10MB
                part_size = 10 * 1024 * 1024
                parts = []
                
                video_bytes.seek(0)
                part_number = 1
                while True:
                    data = video_bytes.read(part_size)
                    if not data:
                        break
                    
                    print(f"上传分片 {part_number}")
                    result = bucket.upload_part(filename, upload_id, part_number, data)
                    parts.append(oss2.models.PartInfo(part_number, result.etag))
                    part_number += 1
                
                # 完成分片上传
                bucket.complete_multipart_upload(filename, upload_id, parts)
                print(f"分片上传完成，共 {len(parts)} 个分片")
                
            else:
                # 普通上传
                print(f"文件大小 {file_size_mb:.2f}MB 小于阈值 {multipart_threshold}MB，使用普通上传")
                video_bytes.seek(0)
                bucket.put_object(filename, video_bytes, headers=headers)
            
            print(f'视频成功上传到 OSS，文件名为: {filename}')
            
            if use_temporary_url == "是":
                # 生成带有过期时间的临时URL
                url = bucket.sign_url('GET', filename, expiration_hours * 3600)  # 转换为秒
                # 确保URL使用https协议
                if url.startswith('http://'):
                    url = 'https://' + url[7:]
                print(f'生成临时URL，过期时间: {expiration_hours}小时')
            else:
                # 构建普通URL
                url = f"https://{bucket_name}.{endpoint}/{filename}"
            
            return url, file_size_mb
            
        except oss2.exceptions.OssError as e:
            raise ValueError(f'视频上传失败，错误信息: {e}')
        except Exception as e:
            raise ValueError(f'视频处理失败，错误信息: {e}')

# 节点映射字典
NODE_CLASS_MAPPINGS = {
    "OSSVideoUploadNode": OSSVideoUploadNode,
    "OSSVideoAdvancedUploadNode": OSSVideoAdvancedUploadNode
}

# 节点显示名称映射字典
NODE_DISPLAY_NAME_MAPPINGS = {
    "OSSVideoUploadNode": "视频上传到OSS",
    "OSSVideoAdvancedUploadNode": "高级视频上传到OSS"
}