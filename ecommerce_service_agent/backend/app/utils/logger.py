import sys
from loguru import logger
from app.core.config import settings

"""
日志配置模块 - 使用 loguru 提供统一的日志记录
"""
def setup_logger():
    """配置日志格式和输出"""
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    console_level = "DEBUG" if settings.DEBUG else "INFO"
    logger.add(sys.stdout, format=log_format, level=console_level, colorize=True)
    logger.add(
        "logs/ecommerce-cs.log",
        format=log_format,
        rotation="100 MB",
        retention="30 days",
        level="INFO",
        encoding="utf-8"
    )

    return logger


log = setup_logger()