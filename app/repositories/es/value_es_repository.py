"""
用于操作Elasticsearch全文索引库的持久层类  专门处理字段值数据
接收参数： 能进行Elasticsearch的存储和搜索的client对象     AsyncElasticsearch类型
"""
from elasticsearch import AsyncElasticsearch

from app.models.es.value_info_es import ValueInfoES


class ValueESRepository:
    # 将索引名称和映射关系抽离成类属性方便使用
    index_name = "data-agent-value-index2"
    index_mapping = {
        # 禁用动态映射，防止新增字段时自动映射
        "dynamic": False,
        # 只需要对字段值建立索引，其他属性不需要
        "properties": {
            "id":{"type":"keyword","index":False},
            "value":{"type":"text","analyzer":"ik_max_word"},
            "type":{"type":"keyword","index":False},
            "column_id":{"type":"keyword","index":False},
            "column_name":{"type":"keyword","index":False},
            "table_id":{"type":"keyword","index":False},
            "table_name":{"type":"keyword","index":False}
        }
    }

    def __init__(self,client:AsyncElasticsearch):
        self.client = client

    # 创建索引库
    async def create_index(self):
        client = self.client
        index_name = self.index_name
        # 如果存在先删除，方便多次测试
        if await client.indices.exists(index=index_name):
            await client.indices.delete(index=index_name)
        await client.indices.create(
            index=index_name,
            mappings=self.index_mapping
        )

    # 批量保存多个字段值信息列表到es库
    async def insert_value_infos(self,value_infos:list[ValueInfoES]):
        # 创建索引，单独封装成方法，直接调用
        await self.create_index()

        # 分批次保存数据
        # 本项目中共110条数据，所以按每批次50条进行保存。实际情况根据数据量进行调整
        batch_size = 50
        for i in range(0,len(value_infos),batch_size):
            batch_value_infos = value_infos[i:i+batch_size]

            # 根据value_infos收集信息生成operations
            operations = []
            for value_info in batch_value_infos:
                # 这里不能直接保存value_info,需要先保存索引信息
                operations.append(
                    {
                        "index": {
                            "_index": self.index_name,
                        }
                    }
                )
                operations.append(value_info)

            # 批量插入多个文档
            await self.client.bulk(
                operations=operations
            )