"""
ContextVar: 协程安全的上下文变量
    每个协程都有自己的上下文对象，互不干扰，可以向其中独立设置和获取不同变量名的数据
        =》协程1：context对象：{"aa": 数据1， "bb": 数据2}
        =》协程2：context对象：{"aa": 数据3， "bb": 数据4}
    我们可以通过ContextVar向当前协程的context对象中设置数据和获取数据
    注意：ContextVar对象本身并不存储数据，数据存储在协程的context对象中 =》contextVar是多个context对象的代理对象
"""
import asyncio
from _contextvars import ContextVar, Token

# 创建一个用于存取请求id的context_var对象，测试时可以给一个指定的默认值，正式使用时默认值为空字符串
_request_id_context_var = ContextVar("request_id", default="aaa")
# 获取当前协程的请求id
def get_request_id():
    return _request_id_context_var.get()

# 设置当前协程的请求id
def set_request_id(request_id:str)->Token:
    # _request_id_context_var.set(request_id)
    # 返回一个Token对象
    return _request_id_context_var.set(request_id)

# 重置当前协程的请求id，reset函数需要传参，参数类型为set函数的返回值类型
def reset_request_id(token:Token):
    _request_id_context_var.reset(token)


# 测试
if __name__ == "__main__":
    async def req1():
        # 获取当前协程的请求id
        print("当前协程1的请求id:", get_request_id())
        # 设置当前协程的请求id
        token = set_request_id("1234")
        await asyncio.sleep(1)
        print("设置请求id后，当前协程1的请求id:", get_request_id())
        # 重置当前协程的请求id
        await asyncio.sleep(1)
        reset_request_id(token)
        print("重置请求id后，当前协程1的请求id:", get_request_id())


    async def req2():
        # 获取当前协程的请求id
        print("当前协程2的请求id:", get_request_id())
        # 设置当前协程的请求id
        token = set_request_id("5678")
        await asyncio.sleep(1)
        print("设置请求id后，当前协程2的请求id:", get_request_id())
        # 重置当前协程的请求id
        await asyncio.sleep(1)
        # reset_request_id(token)
        print("重置请求id后，当前协程2的请求id:", get_request_id())

    async def test():
        await asyncio.gather(req1(), req2())

    asyncio.run(test())

