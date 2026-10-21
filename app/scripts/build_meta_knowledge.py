"""
构建元数据知识库的入口脚本文件
"""
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.core.log import logger
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.services.meta_knowledge_service import MetaKnowledgeService


async def start_build():
    """
    启动构建的函数
    1. 初始化客户端
    2. 创建业务层对象（先创建会话，持久层对象）
    3. 调用构建的业务方法进行构建处理
    4. 成功了，提交事务；失败了，回滚事务
    5. 无论成功失败，都要关闭客户端
    """
    logger.info("开始构建元数据知识库")
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
            # 创建业务层对象
            service = MetaKnowledgeService(
                dw_mysql_repository=DWMysqlRepository(dw_session),
                meta_mysql_repository=MetaMysqlRepository(meta_session),
                column_qdrant_repository=ColumnQdrantRepository(qdrant_client_manager.client),
                metric_qdrant_repository=MetricQdrantRepository(qdrant_client_manager.client),
                value_es_repository=ValueESRepository(es_client_manager.client),
                embedding_client=embedding_client_manager.client
            )
            # 调用业务层对象构建的业务方法
            await service.build()

            # 处理完成，提交事务
            # dw_session可以不用处理，原因：dw库只有查询，不需要事务
            # await dw_session.commit()
            await meta_session.commit()
            logger.info("元数据知识库构建完成")
    except Exception as e:
        logger.error("元数据知识库构建失败", e)
        # 处理失败，回滚事务
        # await dw_session.rollback()
        await meta_session.rollback()
        raise # 抛出异常，打印更多异常信息
    finally:
        # 无论成功还是失败，都要关闭客户端
        await dw_mysql_client_manager.close()
        await meta_mysql_client_manager.close()
        await qdrant_client_manager.close()
        await es_client_manager.close()


if __name__ == '__main__':
    asyncio.run(start_build())