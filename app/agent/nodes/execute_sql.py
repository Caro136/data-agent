from asyncio.log import logger

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


async def execute_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 自定义输出内容
    runtime.stream_writer("执行SQL")

    try:
        # 业务处理
        return {}
    except Exception as e:
        logger.error(f"执行SQL失败, {str(e)}")
        raise