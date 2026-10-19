"""
用来操作Qdrant库的客户端管理模块
"""
import asyncio
import random
import uuid

from qdrant_client import AsyncQdrantClient, models

from app.conf.app_config import QdrantConfig, app_config


class QdrantClientManager:
    def __init__(self,config:QdrantConfig):
        self.config = config
        self.client:AsyncQdrantClient | None = None

    def init_client(self):
        self.client = AsyncQdrantClient(f"http://{self.config.host}:{self.config.port}")

    async def close(self):
        await self.client.close()

# 创建实例
qdrant_client_manager = QdrantClientManager(app_config.qdrant)

# 测试
if __name__ == '__main__':
    async def test():
        # 初始化客户端
        qdrant_client_manager.init_client()
        # 获取客户端
        client = qdrant_client_manager.client
        # 定义集合名称
        collection_name = "test_collection"

        # 创建集合，如果不存在才创建 =》 适用于正式运行时
        # if not await client.collection_exists(collection_name):
        #     await client.create_collection(
        #         collection_name=collection_name, # 集合的名称
        #         # 向量的配置
        #         vectors_config=models.VectorParams(
        #             size=app_config.qdrant.embedding_size, # 向量的维度
        #             distance=models.Distance.COSINE # 向量的距离度量方式：余弦相似度
        #         )
        #     )

        # 创建集合，如果存在则先删除 =》 适用于开发测试时
        if await client.collection_exists(collection_name):
            await client.delete_collection(collection_name)
        await client.create_collection(
            collection_name=collection_name, # 集合的名称
            # 向量的配置
            vectors_config=models.VectorParams(
                size=app_config.qdrant.embedding_size, # 向量的维度
                distance=models.Distance.COSINE # 向量的距离度量方式：余弦相似度
            )
        )

        # 批量插入多个向量
        await client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=uuid.uuid4(), # id保证唯一性，也可以直接用id=i
                    vector=[random.random() for i in range(1024)], # 生成1024维随机向量
                    payload={"color": "white" if i % 2 == 0 else "black"}, # 向量的元数据，一半白色，一半黑色进行区分
                )
                for i in range(10) # 创建10个向量
            ]
        )

        # 搜索
        result = await client.query_points(
            collection_name=collection_name,
            query=[random.random() for i in range(1024)],
            limit=5, # 取TOP3
            score_threshold=0.6, # 相似度得分的最小值
            # 根据payload进行过滤
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="color",
                        match=models.MatchValue(value="white")
                    )
                ]
            )
        )
        points = result.points
        print(points)
        for point in points:
            print(point.payload)

        # 关闭客户端
        await qdrant_client_manager.close()

    # 调用
    asyncio.run(test())
