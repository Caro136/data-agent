"""
用于操作mysql数据仓库（dw库）数据的持久层模块
接收的参数：能执行数据库操作的session对象： AsyncSession类型
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
class DWMysqlRepository:
    def __init__(self,session:AsyncSession):
        self.session = session

    # 查询指定表的所有字段的类型：dict[字段名，字段类型]
    async def get_column_types(self, table_name:str)->dict[str,str]:
        sql = f"show columns from {table_name}"
        result = await self.session.execute(text(sql))
        return {item.Field:item.Type for item in result.all()}

    # 查询指定表中的指定字段的指定数量的字段值，默认10个
    async def get_column_values(self, table_name:str, column_name:str, limit:int=10)->list:
        sql = f"select distinct {column_name} from {table_name} limit {limit}"
        result = await self.session.execute(text(sql))
        # 获取单个字段用scalars()
        return result.scalars().all() # [val, val]