#                  大模型项目之<<掌柜问数>>

# 1. 运行项目测试

## 1.1. 项目代码说明

- `data-agent`：后端项目
- `data-agent_frontend`：前端项目
- `docker`：后端支撑服务（mysql数据库、qdrant向量索引库和es全文索引库）

## 1.2. 通过docker安装中间件启动服务

- 启动`windows版本docker`（docker desktop）


- 加载安装本地镜像

  ```
  ...\3.代码\docker> docker load -i all-images.tar
  ```

![image-20260901075200128](https://gitee.com/caorong180/typora_pictures/raw/master/img/2026/image-20260901075200128.png)


  ![image-20260820093448881](https://gitee.com/caorong180/typora_pictures/raw/master/img/2026/image-20260820093448881-17881349292211.png)

- 停止已有的mysql服务（前期课程安装自动启动的）

  ```
  - 停止原有的mysql服务（前期课程安装自动启动的）： 任务管理器 -> 服务 -> MYSQL服务 -> 右键“停止”
  - 将原有的mysql服务的启动方式设置为手动：MYSQL服务 -> 右键“打开服务” -> MYSQL服务 -> 右键“属性”设置为手动
  ```

- 启动容器服务

  ```
  ...\3.代码\docker> docker compose up -d
  ```

  ![image-20260820092602269](https://gitee.com/caorong180/typora_pictures/raw/master/img/2026/image-20260820092602269-17881349292212.png)

  ![image-20260820093628407](https://gitee.com/caorong180/typora_pictures/raw/master/img/2026/image-20260820093628407.png)



## 1.3. 构建知识库

- 进入后端项目目录data-agent，运行构建脚本`app/scripts/build_meta_knowledge.py`

  ```
  ...\3.代码\data-agent> uv sync
  ...\3.代码\data-agent> uv run -m app.scripts.build_meta_knowledge
  ```

## 1.4. 运行后端项目

- 进入后端项目目录data-agent，运行启动脚本`main.py`

  ```
  ...\3.代码\data-agent> uv run -m main
  ```

  

## 1.5. 运行前端项目

- 进入前端项目目录data-agent_frontend，执行启动命令

  ```
  ...\3.代码\data-agent_frontend> npm run dev
  ```

  

## 1.6. 访问测试

- 浏览器上访问： http://127.0.0.1:5173/
- 搜索相关问题
  - 华北地区销售总额
  - 2025年各地区平均销售额
  - 各个地区iPhone去年卖了多少钱