"""
工具函数模块
导出所有工具函数
"""
from utils.time_utils import now_china, utcnow, sync_time_to_china, format_datetime, parse_datetime
from utils.file_utils import (
    allowed_file, get_file_extension, get_file_category,
    is_image_file, is_document_file, ensure_directory, get_safe_filename,
    ALLOWED_EXTENSIONS, IMAGE_EXTENSIONS, DOCUMENT_EXTENSIONS, SPREADSHEET_EXTENSIONS
)
from utils.permission_utils import (
    require_permission, require_login, require_admin,
    get_current_user, check_user_permission
)

__all__ = [
    # 时间工具
    'now_china',
    'utcnow',
    'sync_time_to_china',
    'format_datetime',
    'parse_datetime',
    # 文件工具
    'allowed_file',
    'get_file_extension',
    'get_file_category',
    'is_image_file',
    'is_document_file',
    'ensure_directory',
    'get_safe_filename',
    'ALLOWED_EXTENSIONS',
    'IMAGE_EXTENSIONS',
    'DOCUMENT_EXTENSIONS',
    'SPREADSHEET_EXTENSIONS',
    # 权限工具
    'require_permission',
    'require_login',
    'require_admin',
    'get_current_user',
    'check_user_permission',
]
