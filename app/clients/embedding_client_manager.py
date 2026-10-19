"""
Embedding客户端管理
用于管理 HuggingFaceEndpointEmbeddings 客户端的初始化和配置
"""
import asyncio
from typing import Optional

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.conf.app_config import EmbeddingConfig, app_config


class EmbeddingClientManager:
    def __init__(self,config:EmbeddingConfig):
        self.config = config
        # Optional[HuggingFaceEndpointEmbeddings]可选操作，等效于HuggingFaceEndpointEmbeddings | None
        self.client:Optional[HuggingFaceEndpointEmbeddings] = None

    def init_client(self):
        self.client = HuggingFaceEndpointEmbeddings(model=f"http://{self.config.host}:{self.config.port}")

    # 这里HuggingFaceEndpointEmbeddings的client没有close方法，会自动关闭，不需要手动声明

# 创建实例
embedding_client_manager = EmbeddingClientManager(app_config.embedding)

# 测试
if __name__ == '__main__':
    async def test():
        embedding_client_manager.init_client()

        # 生成一个向量，向量类型为list[float]
        vector:list[float] = await embedding_client_manager.client.aembed_query("hello")
        print(vector)
        print(len(vector)) # 1024

        # 批量生成多个向量
        vectors:list[list[float]] = await embedding_client_manager.client.aembed_documents(["hello","world"])
        print(vectors)
        print(len(vectors),len(vectors[0])) # 2 1024

    # 调用
    asyncio.run(test())