# ComfyUI OSS上传插件

这是一个用于ComfyUI的阿里云OSS上传插件，可以直接将生成的图片上传到阿里云OSS存储服务中。

## 功能

- **自动保存图片到OSS**：基础的OSS上传节点，自动生成文件名
- **高级OSS上传**：高级选项的OSS上传节点，支持更多设置

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

自动生成的文件名格式为：`[文件夹]/[前缀]_[时间戳]_[序号]_[随机ID].jpg`

### 高级OSS上传节点

高级版节点提供了更多的自定义选项：

- 基本参数与基本节点相同
- **format**：图片格式（JPEG、PNG、WEBP）
- **include_date**：是否在文件名中包含日期时间
- **quality**：图片质量（1-100）

## 示例使用方法

1. 在ComfyUI工作流中找到"API/oss"分类
2. 添加"自动保存图片到OSS"或"高级OSS上传"节点
3. 设置阿里云OSS账户信息（access_key_id、access_key_secret、bucket_name等）
4. 连接图像输出到此节点
5. 运行工作流，图像将自动上传到您的OSS存储桶中

## 其他说明

- 上传成功后，节点将返回上传图片的OSS URL
- 请确保您的阿里云帐户有足够的权限上传文件
- 为了安全起见，建议使用有限权限的RAM用户进行OSS操作

## 代码说明

- `oss_upload.py`：基本OSS上传节点
- `oss_upload_options.py`：高级OSS上传节点 
- `oss_utils.py`：共用工具函数

## 故障排除

如遇上传失败，请检查：

1. OSS凭证是否正确
2. 网络连接是否正常
3. 存储桶是否存在并有正确权限
4. 查看终端输出的详细错误信息 