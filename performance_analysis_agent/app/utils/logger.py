import logging
import sys

from app.core.config import settings


def setup_logger(name: str="bank_agent_system")-> logging.Logger:
    """配置并返回 logger 实例"""
    logger = logging.getLogger(name)
    # 设置日志级别
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)

    # 文件处理器（写入 agent_system.log）
    file_handler = logging.FileHandler("agent_system.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# 全局默认 logger
default_logger = setup_logger()