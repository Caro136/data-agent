import asyncio

from langgraph.constants import START, END
from langgraph.graph import StateGraph

from app.agent.context import DataAgentContext
from app.agent.nodes.add_extra_context import add_extra_context
from app.agent.nodes.correct_sql import correct_sql
from app.agent.nodes.execute_sql import execute_sql
from app.agent.nodes.extract_keywords import extract_keywords
from app.agent.nodes.filter_metric import filter_metric
from app.agent.nodes.filter_table import filter_table
from app.agent.nodes.generate_sql import generate_sql
from app.agent.nodes.recall_column import recall_column
from app.agent.nodes.recall_metric import recall_metric
from app.agent.nodes.recall_value import recall_value
from app.agent.nodes.merge_retrieved_info import merge_retrieved_info
from app.agent.nodes.validate_sql import validate_sql
from app.agent.state import DataAgentState

from sqlalchemy.ext.asyncio import AsyncSession
from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
# 创建图对象
state_graph = StateGraph(
    state_schema=DataAgentState,
    context_schema=DataAgentContext,
)
# 添加节点
state_graph.add_node("extract_keywords",extract_keywords)
state_graph.add_node("recall_column", recall_column)
state_graph.add_node("recall_metric", recall_metric)
state_graph.add_node("recall_value", recall_value)
state_graph.add_node("merge_retrieved_info", merge_retrieved_info)
state_graph.add_node("filter_table", filter_table)
state_graph.add_node("filter_metric",filter_metric)
state_graph.add_node("add_extra_context", add_extra_context)
state_graph.add_node("generate_sql", generate_sql)
state_graph.add_node("validate_sql", validate_sql)
state_graph.add_node("correct_sql", correct_sql)
state_graph.add_node("execute_sql", execute_sql)
# 添加边
state_graph.add_edge(START, "extract_keywords")
state_graph.add_edge("extract_keywords", "recall_column")
state_graph.add_edge("extract_keywords", "recall_metric")
state_graph.add_edge("extract_keywords", "recall_value")
state_graph.add_edge("recall_column", "merge_retrieved_info")
state_graph.add_edge("recall_metric", "merge_retrieved_info")
state_graph.add_edge("recall_value", "merge_retrieved_info")
state_graph.add_edge("merge_retrieved_info", "filter_table")
state_graph.add_edge("merge_retrieved_info", "filter_metric")
state_graph.add_edge("filter_table", "add_extra_context")
state_graph.add_edge("filter_metric", "add_extra_context")
state_graph.add_edge("add_extra_context", "generate_sql")
state_graph.add_edge("generate_sql", "validate_sql")
# 添加推荐边
state_graph.add_conditional_edges(
    "validate_sql",
    lambda state: "execute_sql" if state.get("error") is None else "correct_sql",
    {"execute_sql": "execute_sql", "correct_sql": "correct_sql"},
)
state_graph.add_edge("correct_sql", "validate_sql")
state_graph.add_edge("execute_sql", END)

# 编译图对象
compiled_graph = state_graph.compile()
# 绘制图结构
# print(compiled_graph.get_graph().draw_ascii()) # 需要安装依赖
print(compiled_graph.get_graph().draw_mermaid())

# 执行测试
if __name__ == '__main__':
    async def test():
        # 初始化客户端
        dw_mysql_client_manager.init_client()
        meta_mysql_client_manager.init_client()
        qdrant_client_manager.init_client()
        es_client_manager.init_client()
        embedding_client_manager.init_client()

        try:
            # 创建会话
            # 指定session类型：方式一：断言有值
            assert dw_mysql_client_manager.session_factory
            async with (
                dw_mysql_client_manager.session_factory() as dw_session,
                meta_mysql_client_manager.session_factory() as meta_session
            ):
                # 方式二：直接指定类型
                meta_session: AsyncSession
                # 创建状态对象
                state = DataAgentState(query="华北地区销售总金额")
                # 创建上下文对象
                context = DataAgentContext(
                    dw_mysql_repository=DWMysqlRepository(dw_session),
                    meta_mysql_repository=MetaMysqlRepository(meta_session),
                    column_qdrant_repository=ColumnQdrantRepository(qdrant_client_manager.client),
                    metric_qdrant_repository=MetricQdrantRepository(qdrant_client_manager.client),
                    value_es_repository=ValueESRepository(es_client_manager.client),
                    embedding_client=embedding_client_manager.client
                )
                async for chunk in compiled_graph.astream(
                        input=state,
                        context=context,
                        # stream_mode="updates"  # 执行得到的是每个节点返回的状态更新  默认
                        # stream_mode="values"  # 执行得到的是节点返回合并后state的值
                        stream_mode="custom",  # 执行得到是节点中指定的自定义输出
                ):
                    print("---", chunk)

        except Exception as e:
            print("搜索失败", e)

            raise  # 抛出异常，打印更多异常信息
        finally:
            # 无论成功还是失败，都要关闭客户端
            await dw_mysql_client_manager.close()
            await meta_mysql_client_manager.close()
            await qdrant_client_manager.close()
            await es_client_manager.close()

    asyncio.run(test())