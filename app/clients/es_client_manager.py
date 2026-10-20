"""
用来操作ES数据库的客户端管理器模块
"""
import asyncio
from typing import Optional

from elasticsearch import AsyncElasticsearch

from app.conf.app_config import ESConfig, app_config


class ESClientManager:
    def __init__(self,config:ESConfig):
        self.config = config
        self.client:Optional[AsyncElasticsearch] = None

    def init_client(self):
        self.client = AsyncElasticsearch(
        # es支持多个集群服务，所以这里可以传入多个url链接。但本项目只有一个
        hosts=[f"http://{self.config.host}:{self.config.port}"]
        # 这里没有设置api_key，是因为docker配置文件中相关参数设置了false
        # api_key = os.getenv("ELASTIC_API_KEY"),
    )

    async def close(self):
        await self.client.close()

# 创建实例
es_client_manager = ESClientManager(app_config.es)

# 测试
if __name__ == '__main__':
    async def test():
        es_client_manager.init_client()
        client = es_client_manager.client

        index_name = "my-books"

        # 创建索引
        # 如果索引存在则先删除，适用于开发测试
        if await client.indices.exists(index=index_name):
            await client.indices.delete(index=index_name)
        await client.indices.create(
            index=index_name,
            mappings={
                # 使用静态映射
                "dynamic": False,
                # 属性名称和类型
                "properties": {
                    "name": {
                        "type": "text"
                    },
                    "author": {
                        "type": "text"
                    },
                    "release_date": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "page_count": {
                        "type": "integer"
                    }
                }
            }
        )
        # 批量插入数据
        await client.bulk(
            operations=[
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "Revelation Space",
                    "author": "Alastair Reynolds",
                    "release_date": "2000-03-15",
                    "page_count": 585
                },
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "1984",
                    "author": "George Orwell",
                    "release_date": "1985-06-01",
                    "page_count": 328
                },
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "Fahrenheit 451",
                    "author": "Ray Bradbury",
                    "release_date": "1953-10-15",
                    "page_count": 227
                },
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "Brave New World",
                    "author": "Aldous Huxley",
                    "release_date": "1932-06-01",
                    "page_count": 268
                },
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "The Handmaids Tale",
                    "author": "Margaret Atwood",
                    "release_date": "1985-06-01",
                    "page_count": 311
                }
            ],
        )
        # 立即刷新保存到数据库中（默认1秒后才保存，所以不设置的时候执行代码查询不到）
        await client.indices.refresh(index=index_name)
        # 查询
        resp = await client.search(
            index=index_name,
            query={
                # 根据name属性进行分词匹配查询
                "match": {
                    "name": "brave"
                }
            },
        )
        # 读取数据
        print(resp)
        print(resp["hits"]["hits"][0]["_source"])
        # 关闭
        await es_client_manager.close()

    asyncio.run(test())