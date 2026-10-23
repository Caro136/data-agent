"""
操作Qdrant向量索引库的持久层类  专门处理字段信息数据
接收参数： 能进行Qdrant的存储和搜索的client对象     AsyncQdrantClient类型
"""
from qdrant_client import models
from qdrant_client import AsyncQdrantClient

from app.conf.app_config import app_config
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant


class ColumnQdrantRepository:
    collection_name = "data-agent-column-collection2"

    def __init__(self,client:AsyncQdrantClient):
        self.client = client

    # 创建集合，单独封装方法
    async def create_collection(self):
        client = self.client
        collection_name = self.collection_name
        # 如果集合存在先删除，便于测试
        if await client.collection_exists(collection_name):
            await client.delete_collection(collection_name)
        await client.create_collection(
            collection_name=collection_name,
            # 向量配置
            vectors_config=models.VectorParams(
                size=app_config.qdrant.embedding_size, # 向量维度
                distance=models.Distance.COSINE # 余弦相似度
            ),
        )

    # 批量插入多个字段信息的向量列表
    async def insert_column_vectors(self,ids:list[str],payloads:list[ColumnInfoQdrant],vectors:list[list[float]]):
        # 创建集合
        await self.create_collection()

        # 分批处理，每次处理20条数据
        batch_size = 20
        for i in range(0,len(ids),batch_size):
            batch_ids = ids[i:i+batch_size]
            batch_payloads = payloads[i:i+batch_size]
            batch_vectors = vectors[i:i+batch_size]
            # 批量插入多个向量
            await self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=batch_ids[i],
                        payload=batch_payloads[i],
                        vector=batch_vectors[i]
                    ) for i in range(len(batch_ids))
                ],
            )

    # 搜索
    async def search(self, keyword_vector:list[float])->list[ColumnInfoQdrant]:
        result = await self.client.query_points(
            collection_name=self.collection_name,
            query=keyword_vector,
            # 相似度得分最小值，需要反复测试来确定这个值
            score_threshold=0.6
        )
        # 读取payload数据列表返回，这里需要将字典转换为对象，可以直接用解包，也可以手动进行转换
        return [ColumnInfoQdrant(**point.payload) for point in result.points]
