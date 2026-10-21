from typing import TypedDict

# 自定义状态，继承类型字典，方便与json进行转换
class DataAgentState(TypedDict):
    query:str # 用户查询
    keywords:list[str] # 分词列表
    sql:str # 生成sql
    error:str # 校验失败的错误信息