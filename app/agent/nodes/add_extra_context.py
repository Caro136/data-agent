from asyncio.log import logger

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


async def add_extra_context(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 自定义输出内容
    runtime.stream_writer("添加额外上下文")

    try:
        # 业务处理
        return {}
    except Exception as e:
        logger.error(f"添加额外上下文失败, {str(e)}")
        raise