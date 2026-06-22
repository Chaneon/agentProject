import sys
import logger
from models.config import settings
"""
日志配置模块：使用 loguru 提供统一的日志记录
"""
def setup_logger():
    logger.remove()
    log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    logger.add(sys.stdout, format=log_format, level="DEBUG" if settings.debug else "INFO")
    logger.add("logs/python-service.log", rotation="100 MB", retention="7 days", format=log_format, level="INFO")
    return logger

# 全局默认 logger
default_logger = setup_logger()