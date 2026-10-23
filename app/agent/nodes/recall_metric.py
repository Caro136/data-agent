
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant
from app.prompt.prompt_loader import load_prompt

"""
1. 使用大模型对query语义化提取关键词列表，与前面jieba提取关键词进行去重合并 =》 keywords:list[str]
2. 将所有keywords进行批量向量化 =》 keyword_vectors: list[list[float]]
3. 遍历每个关键词向量，去Qdrant中匹配出一个指标信息列表， 并进行去重合并 =》 recall_metrics: list[MetricInfoQdrant]
4. 返回recall_metrics
"""
async def recall_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 自定义输出内容
    runtime.stream_writer("召回指标")

    try:
        query = state["query"]
        keywords = state["keywords"]
        embedding_client = runtime.context["embedding_client"]
        metric_qdrant_repo = runtime.context["metric_qdrant_repository"]

        # 1.使用大模型对query语义化提取关键词列表，与前面jieba提取关键词进行去重合并 =》 keywords:list[str]
        prompt_template = PromptTemplate(
            template=load_prompt("extend_keywords_for_metric_recall"),
            input_variables=["query"],
        )
        output_parser = JsonOutputParser()
        chain = prompt_template | llm | output_parser
        result:list[str] = await chain.ainvoke({"query": query})
        logger.info(f"recall_metric llm keywords = {result}")
        keywords = list(set(keywords + result))

        # 2.将所有keywords进行批量向量化 =》 keyword_vectors: list[list[float]]
        keyword_vectors:list[list[float]] = await embedding_client.aembed_documents(keywords)

        # 3.遍历每个关键词向量，去Qdrant中匹配出一个指标信息列表， 并进行去重合并 =》 recall_metrics: list[MetricInfoQdrant]
        metric_info_dict:dict[str, MetricInfoQdrant] = {}
        for keyword_vector in keyword_vectors:
            metric_infos:list[MetricInfoQdrant] = await metric_qdrant_repo.search(keyword_vector)
            for metric_info in metric_infos:
                # 字典格式如果重复会自动覆盖，所以这里不需要对metric_info["id"]进行判断
                metric_info_dict[metric_info["id"]] = metric_info
        # 生成列表
        recall_metrics:list[MetricInfoQdrant] = list(metric_info_dict.values())
        logger.info(f"召回指标完成： {recall_metrics}")
        # 4.返回recall_metrics
        return {"recall_metrics": recall_metrics}
    except Exception as e:
        logger.error(f"召回指标失败, {str(e)}")
        raise