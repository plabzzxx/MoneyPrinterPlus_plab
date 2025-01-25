import os
import logging
from datetime import datetime

# 获取项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(ROOT_DIR, "logs")

# 确保日志目录存在
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_error_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.ERROR)
    
    # 创建文件处理器
    log_file = os.path.join(LOG_DIR, "publish_errors.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    
    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    return logger

# 创建发布错误日志记录器
publish_error_logger = setup_error_logger('publish_error')

def log_publish_error(platform, video_file, error):
    """记录发布错误信息"""
    error_msg = f"Platform: {platform}, File: {os.path.basename(video_file)}, Error: {str(error)}"
    publish_error_logger.error(error_msg) 