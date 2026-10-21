"""
用于操作mysql元数据库（meta库）数据的持久层模块
接收的参数：能执行数据库操作的session对象： AsyncSession类型
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mysql.column_metric_mysql import ColumnMetricMySQL
from app.models.mysql.metric_info_mysql import MetricInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.models.mysql.column_info_mysql import ColumnInfoMySQL


class MetaMysqlRepository:
    def __init__(self,session:AsyncSession):
        self.session = session

    # 向table_info表中添加多条数据
    def save_table_infos(self, table_infos:list[TableInfoMySQL]):
        self.session.add_all(table_infos)

    # 向column_info表中添加多条数据
    def save_column_infos(self, column_infos:list[ColumnInfoMySQL]):
        self.session.add_all(column_infos)

    # 向metric_info表中添加多条数据
    def save_metric_infos(self, metric_infos:list[MetricInfoMySQL]):
        self.session.add_all(metric_infos)

    # 向column_metric表中添加多条数据
    def save_column_metrics(self, column_metrics:list[ColumnMetricMySQL]):
        self.session.add_all(column_metrics)