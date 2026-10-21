"""
操作Qdrant向量索引库的持久层类  专门处理字段信息数据
接收参数： 能进行Qdrant的存储和搜索的client对象     AsyncQdrantClient类型
"""
from qdrant_client import AsyncQdrantClient
class ColumnQdrantRepository:
    def __init__(self,client:AsyncQdrantClient):
        self.client = client