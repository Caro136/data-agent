"""
构建元数据知识库的核心业务模块
"""
from langchain_huggingface import HuggingFaceEmbeddings

from app.conf.meta_config import meta_config, TableConfig, MetricConfig
from app.core.log import logger
from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.column_metric_mysql import ColumnMetricMySQL
from app.models.mysql.metric_info_mysql import MetricInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


class MetaKnowledgeService:
    def __init__(
        self,
        dw_mysql_repository: DWMysqlRepository,
        meta_mysql_repository: MetaMysqlRepository,
        column_qdrant_repository: ColumnQdrantRepository,
        metric_qdrant_repository: MetricQdrantRepository,
        value_es_repository: ValueESRepository,
        embedding_client:HuggingFaceEmbeddings
    ):
        self.dw_mysql_repository = dw_mysql_repository
        self.meta_mysql_repository = meta_mysql_repository
        self.column_qdrant_repository = column_qdrant_repository
        self.metric_qdrant_repository = metric_qdrant_repository
        self.value_es_repository = value_es_repository
        self.embedding_client = embedding_client

    async def build(self):
        """
            构建元数据知识的业务方法：
                1. 处理表和字段的信息数据
                1.1. 将所有表和字段的信息添加到meta库
                1.2. 将字段信息添加到qdrant建立向量索引
                1.3. 将字段值信息添加到es建立全文索引
                2. 处理指标的信息数据
                2.1. 将指标信息添加到meta库
                2.2. 将指标信息添加到qdrant建立向量索引
        """
        logger.info("开始构建元数据知识库")
        # 1.处理表和字段的信息数据
        #   1.1 将所有表和字段的信息添加到meta库（table_info表和column_info表）
        column_infos:list[ColumnInfoMySQL] = await self._save_table_infos_to_meta(meta_config.tables)
        logger.info("将所有表和字段的信息添加到meta库完成")
        #   1.2 将字段信息添加到qdrant建立向量索引
        await self._save_column_infos_to_qdrant(column_infos)
        logger.info("将字段信息添加到qdrant建立向量索引完成")
        #   1.3 将字段值信息添加到es库建立全文索引
        await self._save_column_values_to_es(column_infos,meta_config.tables)
        logger.info("将字段值信息添加到es库建立全文索引完成")

        # 2.处理指标的信息数据
        #   2.1 将指标信息添加到meta库(metric_info表和column_metric表)
        metric_infos:list[MetricInfoMySQL] = await self._save_metric_infos_to_meta(meta_config.metrics)
        logger.info("将指标信息添加到meta库完成")
        #   2.2 将指标信息添加到qdrant建立向量索引
        await self._save_metric_infos_to_qdrant(metric_infos)
        logger.info("将指标信息添加到qdrant建立向量索引完成")

    # 将所有表和字段的信息添加到meta库（table_info表和column_info表）
    async def _save_table_infos_to_meta(self, tables:list[TableConfig])->list[ColumnInfoMySQL]:
        # 遍历tables收集表信息的列表table_info表和字段信息的列表column_info表
        table_infos:list[TableInfoMySQL] = []
        column_infos:list[ColumnInfoMySQL] = []
        for table in tables:
            table_infos.append(
                TableInfoMySQL(
                    id=table.name,
                    name=table.name,
                    role=table.role,
                    description=table.description
                )
            )
            # 查询当前表的所有字段的类型：dict[字段名,字段类型]
            column_types:dict[str,str] = await self.dw_mysql_repository.get_column_types(table.name)
            for column in table.columns:
                # 查询当前字段的前10个值
                values:list = await self.dw_mysql_repository.get_column_values(table.name, column.name)
                column_infos.append(
                    ColumnInfoMySQL(
                        # 不同表可能有相同字段，需要加上表名保证唯一性
                        id=f"{table.name}.{column.name}",
                        name=column.name,
                        type=column_types[column.name], # 需要查询dw库获取
                        role=column.role,
                        examples=values, # 需要查询dw库获取
                        description=column.description,
                        alias=column.alias,
                        table_id=table.name
                    )
                )

        # 保存到meta库
        self.meta_mysql_repository.save_table_infos(table_infos)
        self.meta_mysql_repository.save_column_infos(column_infos)
        # 返回字段信息列表
        return column_infos

    # 将字段信息添加到qdrant建立向量索引
    async def _save_column_infos_to_qdrant(self, column_infos:list[ColumnInfoMySQL]):
        pass

    # 将字段值信息添加到es库建立全文索引
    async def _save_column_values_to_es(self, column_infos:list[ColumnInfoMySQL], tables:list[TableConfig]):
        pass



    # 将指标信息添加到meta库(metric_info表和column_metric表)
    async def _save_metric_infos_to_meta(self, metrics:list[MetricConfig])->list[MetricInfoMySQL]:
        # 1.遍历metrics来收集指标信息metric_info表与字段指标column_metric表
        metric_infos:list[MetricInfoMySQL] = []
        column_metrics:list[ColumnMetricMySQL] = []
        for metric in metrics:
            metric_infos.append(
                MetricInfoMySQL(
                    id=metric.name,
                    name=metric.name,
                    description=metric.description,
                    relevant_columns=metric.relevant_columns,
                    alias=metric.alias
                )
            )
            for column_id in metric.relevant_columns:
                column_metrics.append(
                    ColumnMetricMySQL(
                        metric_id=metric.name,
                        column_id=column_id
                    )
                )
        # 2.保存到meta库
        self.meta_mysql_repository.save_metric_infos(metric_infos)
        self.meta_mysql_repository.save_column_metrics(column_metrics)

        return metric_infos

    # 将指标信息添加到qdrant建立向量索引
    async def _save_metric_infos_to_qdrant(self, metric_infos:list[MetricInfoMySQL]):
        pass