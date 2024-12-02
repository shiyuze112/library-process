import sys
from functools import wraps
import time
from loguru import logger

def format_record(record):
    # 基础格式
    log_format = "<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> | <level>{level:}</level> | "
    
    if 'project_id' in record["extra"]:
        log_format = f"{log_format}<blue>[{{extra[project_id]}}]</blue> "
    if 'media_id' in record["extra"]:
        log_format = f"{log_format}<green>[{{extra[media_id]}}]</green> "
    if 'media_key' in record["extra"]:
        log_format = f"{log_format}<cyan>[{{extra[media_key]}}]</cyan> "
    
    
    # 添加消息内容和换行符
    log_format += "<cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>{extra[new_line]}"
    
    return log_format


def setup_logger():
    # 移除默认的 handler
    logger.remove()
    logger.configure(extra={"new_line": "\n"})
    # 添加控制台输出
    logger.add(sys.stdout, format=format_record, level="DEBUG")

    # 添加文件输出
    logger.add("logs/app.log", format=format_record, rotation="500 MB", level="DEBUG")

    return logger


# 创建全局 logger 实例
app_logger = setup_logger()


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        app_logger.info(f"{func.__name__} Took {total_time:.4f} seconds")
        return result

    return timeit_wrapper


def async_timeit(func):
    @wraps(func)
    async def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        app_logger.info(f"{func.__name__} Took {total_time:.4f} seconds")
        return result

    return timeit_wrapper
