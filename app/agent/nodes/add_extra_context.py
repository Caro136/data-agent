from asyncio.log import logger
from datetime import datetime

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, DateInfoState, DBInfoState


async def add_extra_context(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 自定义输出内容
    runtime.stream_writer("添加额外上下文")

    try:
        dw_mysql_repo = runtime.context["dw_mysql_repository"]

        # 生成当前日期数据
        today = datetime.today()
        date = today.strftime("%Y-%m-%d")
        weekday = today.strftime("%A")
        quarter = f"Q{(today.month + 2) // 3}" # //向下取整，Q1-Q4
        date_info = DateInfoState(
            date=date, weekday=weekday, quarter=quarter
        )

        # 得到当前数据库信息
        db_info_dict = await dw_mysql_repo.get_db_info()
        db_info: DBInfoState = DBInfoState(**db_info_dict) # 解包转换为DBInfoState对象

        logger.info(f"添加额外信息完成：date_info={date_info}, db_info={db_info}")
        return {"date_info": date_info, "db_info": db_info}
    except Exception as e:
        logger.error(f"添加额外上下文失败, {str(e)}")
        raise