from typing import TypedDict

from app.models.es.value_info_es import ValueInfoES
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant

# 列信息封装实体
class ColumnInfoState(TypedDict):
    name: str
    type: str
    role: str
    examples: list
    description: str
    alias: list[str]

# 表信息封装实体
class TableInfoState(TypedDict):
    name: str
    role: str
    description: str
    columns: list[ColumnInfoState]

# 指标信息封装实体
class MetricInfoState(TypedDict):
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]


# 自定义状态，继承类型字典，方便与json进行转换
class DataAgentState(TypedDict):
    query:str # 用户查询
    keywords:list[str] # 分词列表
    sql:str # 生成sql
    error:str # 校验失败的错误信息

    keywords:list[str] # 提取关键词列表
    recall_columns:list[ColumnInfoQdrant] # 召回字段信息列表
    recall_metrics:list[MetricInfoQdrant] # 召回指标信息列表
    recall_values:list[ValueInfoES] # 召回字段值信息列表
    metric_infos:list[MetricInfoState] # 指标信息状态对象列表
    table_infos:list[TableInfoState] # 合并3路召回产生的表和字段信息列表