from asyncio.log import logger

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


async def recall_value(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 自定义输出内容
    runtime.stream_writer("召回字段值")

    try:
        # 业务处理
        return {}
    except Exception as e:
        logger.error(f"召回字段值失败, {str(e)}")
        raise