from asyncio.log import logger

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


async def merge_retrieved_info(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 自定义输出内容
    runtime.stream_writer("合并召回结果")

    try:
        # 业务处理
        return {}
    except Exception as e:
        logger.error(f"合并召回结果失败, {str(e)}")
        raise