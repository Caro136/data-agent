"""
日志模块封装
# 定制日志输出格式，控制输出级别
# 自动将日志内容保存到日志文件
# 指定日志文件的最大大小，一旦超过自动创建一个新的的文件
# 指定文件的有效期，过了自动删除
# 记录当前日志输出是哪个请求的，记录请求id
"""
import asyncio
import sys
from pathlib import Path

from loguru import logger

from app.conf.app_config import app_config
from app.core.context import get_request_id, set_request_id, reset_request_id

# 配置日志格式
log_format = (
    "<red>{time:YYYY-MM-DD HH:mm:ss.SSS}</red> | "  # 默认是绿色显示日志时间（精确到毫秒），改为红色进行区分
    "<level>{level: <8}</level> | "  # 按级别颜色显示日志级别（左对齐，占8个字符）
    "<magenta>request_id - {extra[request_id]}</magenta> | "  # 品红色显示request_id（从日志extra中获取），没有请求id时先注释掉
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "  # 青色显示日志所在文件、函数、行号
    "<level>{message}</level>"  # 按级别颜色显示日志正文
)

# 移除默认的控制台输出
logger.remove()

# 给日志打补丁，使其在输出每条日志前执行inject_request_id函数，注入request_id
# logger = logger.patch(lambda record: record.update(extra={"request_id": get_request_id()}))
# 等价于具名函数
def inject_request_id(record):
    # record.update(extra={"request_id": get_request_id()})
    record["extra"]["request_id"] = get_request_id()
logger = logger.patch(inject_request_id)


# 添加控制台输出的配置
if app_config.logging.console.enable:
    logger.add(
        sys.stdout, # 标准输出（控制台输出）
        format=log_format, # 输出的格式
        level=app_config.logging.console.level # 指定输出的级别
    )

# 添加文件输出的配置
if app_config.logging.file.enable:
    logger.add(
        Path(app_config.logging.file.path) / "app.log",  # 日志文件路径
        format=log_format,
        level=app_config.logging.file.level,
        rotation=app_config.logging.file.rotation, # 文件最大大小，超过自动创建新的文件
        retention=app_config.logging.file.retention, # 文件有效期，过期自动删除。retention 的清理机制 不是在每次写入时实时检查的，而是在日志文件 轮转（rotation）时 或 程序启动时 才会触发过期清理。
    )

if __name__ == '__main__':
    logger.trace("这是 TRACE 级别的调试信息")  # 不会输出到控制台（控制台是 INFO），但会输出到文件
    logger.debug("这是 DEBUG 级别的调试信息")
    logger.info("服务启动成功")  # 控制台+文件都输出
    logger.success("数据同步完成")  # Loguru 独有级别
    logger.warning("内存使用率超过 80%")
    logger.error("接口调用失败：超时")
    logger.critical("数据库连接中断，服务停止")

    async def req1():
        logger.info(f"1---req1 req_id={get_request_id()}")
        token = set_request_id("1111")
        await asyncio.sleep(1)
        logger.info(f"2---req1 req_id={get_request_id()}")
        await asyncio.sleep(1)
        reset_request_id(token)
        logger.info(f"3---req1 req_id={get_request_id()}")

    async def req2():
        logger.info(f"1---req2 req_id={get_request_id()}")
        await asyncio.sleep(1)
        logger.info(f"2---req2 req_id={get_request_id()}")
        set_request_id("2222")
        await asyncio.sleep(1)
        logger.info(f"3---req2 req_id={get_request_id()}")
        await asyncio.sleep(1)
        logger.info(f"3---req2 req_id={get_request_id()}")

    async def test():
        await asyncio.gather(req1(), req2())

    asyncio.run(test())