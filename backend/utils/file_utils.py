"""
文件处理工具模块
提供文件相关的工具函数
"""
import os

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}

# 图片扩展名
IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# 文档扩展名
DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'rtf'}

# 表格扩展名
SPREADSHEET_EXTENSIONS = {'xls', 'xlsx', 'csv'}


def allowed_file(filename):
    """
    检查文件扩展名是否允许
    
    Args:
        filename: 文件名
        
    Returns:
        bool: 是否允许
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extension(filename):
    """
    获取文件扩展名
    
    Args:
        filename: 文件名
        
    Returns:
        str: 文件扩展名（小写）
    """
    if not filename or '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()


def get_file_category(filename):
    """
    根据文件扩展名获取文件类别
    
    Args:
        filename: 文件名
        
    Returns:
        str: 文件类别（image/document/spreadsheet/other/unknown）
    """
    if not filename:
        return 'unknown'
    
    ext = get_file_extension(filename)
    
    if ext in IMAGE_EXTENSIONS:
        return 'image'
    elif ext in DOCUMENT_EXTENSIONS:
        return 'document'
    elif ext in SPREADSHEET_EXTENSIONS:
        return 'spreadsheet'
    else:
        return 'other'


def is_image_file(filename):
    """
    检查是否为图片文件
    
    Args:
        filename: 文件名
        
    Returns:
        bool: 是否为图片文件
    """
    return get_file_extension(filename) in IMAGE_EXTENSIONS


def is_document_file(filename):
    """
    检查是否为文档文件
    
    Args:
        filename: 文件名
        
    Returns:
        bool: 是否为文档文件
    """
    return get_file_extension(filename) in DOCUMENT_EXTENSIONS


def ensure_directory(directory):
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_safe_filename(filename):
    """
    获取安全的文件名（移除危险字符）
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 安全的文件名
    """
    # 移除路径分隔符和危险字符
    unsafe_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    safe_filename = filename
    for char in unsafe_chars:
        safe_filename = safe_filename.replace(char, '_')
    return safe_filename
