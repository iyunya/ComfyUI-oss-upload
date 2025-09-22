# ComfyUI OSS上传插件

这是一个用于ComfyUI的阿里云OSS上传插件，可以直接将生成的图片和视频上传到阿里云OSS存储服务中。

## 功能

- **自动保存图片到OSS**：基础的OSS上传节点，自动生成文件名
- **高级OSS上传**：高级选项的OSS上传节点，支持更多设置
- **视频上传到OSS**：支持将视频文件上传到OSS（MP4格式）
- **高级视频上传到OSS**：高级视频上传节点，支持分片上传等功能
- **临时URL生成**：支持生成带有过期时间的临时访问URL

## 安装要求

1. 首先需要安装oss2库：

```bash
pip install oss2
```

2. 将此插件目录放到ComfyUI的custom_nodes目录下

## 使用说明

### 基本OSS上传节点

基本版节点提供了最简单的OSS上传功能：

- **image**：要上传的图像
- **prefix**：文件名前缀
- **access_key_id**：阿里云访问密钥ID
- **access_key_secret**：阿里云访问密钥Secret
- **bucket_name**：OSS存储桶名称
- **endpoint**：OSS终端节点URL
- **folder**：上传到OSS的文件夹路径（可选）
- **use_temporary_url**：是否生成临时访问URL（是/否），默认为"否"
- **expiration_hours**：临时URL的过期时间（小时），默认为24小时，范围1-720小时

自动生成的文件名格式为：`[文件夹]/[前缀]_[时间戳]_[序号]_[随机ID].jpg`

### 高级OSS上传节点

高级版节点提供了更多的自定义选项：

- 基本参数与基本节点相同
- **format**：图片格式（JPEG、PNG、WEBP）
- **include_date**：是否在文件名中包含日期时间
- **quality**：图片质量（1-100）

### 视频上传节点

视频上传节点支持将ComfyUI生成的视频上传到OSS：

- **video**：要上传的视频（VIDEO类型输入）
- **prefix**：文件名前缀，默认为"comfyui_video"
- **access_key_id**：阿里云访问密钥ID
- **access_key_secret**：阿里云访问密钥Secret
- **bucket_name**：OSS存储桶名称
- **endpoint**：OSS终端节点URL
- **folder**：上传到OSS的文件夹路径，默认为"video"
- **include_date**：是否在文件名中包含日期时间
- **use_temporary_url**：是否生成临时访问URL（是/否），默认为"否"
- **expiration_hours**：临时URL的过期时间（小时），默认为24小时
- **custom_filename**：自定义文件名（可选）

自动生成的文件名格式为：`[文件夹]/[前缀]_[时间戳]_[随机ID].mp4`

### 高级视频上传节点

高级视频上传节点提供了更多功能：

- 基本参数与视频上传节点相同
- **multipart_threshold**：分片上传阈值（MB），默认100MB，当视频文件大于此值时自动使用分片上传
- **content_type**：视频内容类型，默认为"video/mp4"
- **返回信息**：除了上传URL外，还返回文件大小和上传时间

**注意**：ComfyUI目前只支持MP4格式的视频输出，所有视频都会以MP4格式上传。

## 临时URL功能说明

临时URL功能允许您生成带有过期时间的访问链接：

- 开启方式：将`use_temporary_url`参数设置为"是"
- 过期时间：通过`expiration_hours`参数设置，默认24小时
- 安全性：所有临时URL均使用HTTPS协议，即使原始URL为HTTP
- 适用场景：临时分享、限时访问、增强安全性等

## 示例使用方法

### 图片上传

1. 在ComfyUI工作流中找到"API/oss"分类
2. 添加"自动保存图片到OSS"或"高级OSS上传"节点
3. 设置阿里云OSS账户信息（access_key_id、access_key_secret、bucket_name等）
4. 连接图像输出到此节点
5. 如需临时URL，将"use_temporary_url"设为"是"并设置合适的过期时间
6. 运行工作流，图像将自动上传到您的OSS存储桶中

### 视频上传

1. 在ComfyUI工作流中找到"API/oss"分类
2. 添加"视频上传到OSS"或"高级视频上传到OSS"节点
3. 设置阿里云OSS账户信息
4. 将"Load Video"节点或其他视频生成节点的VIDEO输出连接到视频上传节点
5. 配置上传参数（文件夹、前缀等）
6. 运行工作流，视频将自动转换为MP4格式并上传到OSS

## 其他说明

- 上传成功后，节点将返回上传文件的OSS URL
- 请确保您的阿里云帐户有足够的权限上传文件
- 为了安全起见，建议使用有限权限的RAM用户进行OSS操作
- 临时URL会在指定时间后自动失效，无需手动删除
- 视频文件会自动转换为MP4格式，确保最佳兼容性
- 大视频文件（>100MB）会自动使用分片上传，提高上传成功率

## 代码说明

- `oss_upload.py`：基本OSS上传节点（图片）
- `oss_upload_options.py`：高级OSS上传节点（图片）
- `oss_video_upload.py`：视频上传节点
- `oss_utils.py`：共用工具函数

## 故障排除

如遇上传失败，请检查：

1. OSS凭证是否正确
2. 网络连接是否正常
3. 存储桶是否存在并有正确权限
4. 查看终端输出的详细错误信息
5. 对于视频上传，确保输入的是有效的VIDEO类型数据
6. 检查视频文件大小，过大的文件可能需要更长的上传时间
