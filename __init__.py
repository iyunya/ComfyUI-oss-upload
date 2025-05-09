from .oss_upload import NODE_CLASS_MAPPINGS as OSS_NODE_MAPPINGS
from .oss_upload import NODE_DISPLAY_NAME_MAPPINGS as OSS_DISPLAY_MAPPINGS

from .oss_upload_options import NODE_CLASS_MAPPINGS as OSS_ADVANCED_NODE_MAPPINGS
from .oss_upload_options import NODE_DISPLAY_NAME_MAPPINGS as OSS_ADVANCED_DISPLAY_MAPPINGS

# 合并节点映射
NODE_CLASS_MAPPINGS = {
    **OSS_NODE_MAPPINGS,
    **OSS_ADVANCED_NODE_MAPPINGS
}

# 合并显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    **OSS_DISPLAY_MAPPINGS,
    **OSS_ADVANCED_DISPLAY_MAPPINGS
}

# 定义web前端文件的位置（如果有的话）
WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY'] 