"""
用于操作Elasticsearch全文索引库的持久层类  专门处理字段值数据
接收参数： 能进行Elasticsearch的存储和搜索的client对象     AsyncElasticsearch类型
"""
from elasticsearch import AsyncElasticsearch


class ValueESRepository:
    def __init__(self,client:AsyncElasticsearch):
        self.client = client