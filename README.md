# Parse Engine


> Parse_Engine 它是一个HTML网页信息提取工具，就是从html网页中解析提取出“我们需要的有价值的数据”或者“新的URL链接”的工具。
> 主要功能是对从网页上采集的数据进行分析，格式化，使数据内容转化为更为方便其它应用使用的 `json` 数据内容。
>> 其中使用到的解析工具有：re正则匹配、python自带的html.parser模块以及lxml库，
>> html.parser与lxml为“结构化解析”模式，他们都以DOM树结构为标准，进行标签结构信息的提取。



#### 构建docker镜像

> 在项目目录下执行 `./release.sh` ，拉取最新代码，生成docker镜像，并上传镜像到远程仓库


#### 启动docker容器
> 开发环境：

```shell
docker run -d --rm -it -p 8880:8880 \
-v /opt/log/data_engine:/opt/log/data_engine \
--add-host dev.gsystem.rpc:192.168.1.66 \
--name=data_engine \
hub.ifchange.com/data_group/data_engine:latest python main.py
```

> 测试环境：

```shell
docker run -d --rm -it -p 8880:8880 \
-v /opt/log/data_engine:/opt/log/data_engine \
--name=data_engine \
hub.ifchange.com/data_group/data_engine:latest python main.py -e testing
```

> 执行命令解说：
   `-v /opt/log/data_engine:/opt/log/data_engine` 将容器内的日志文件，映射到时宿主机；
   `--add-host dev.gsystem.rpc:192.168.1.66` 将需要用到的第三方服务的域名映射到时其主机；
   `--name=data_engine` 设置容器名；
   `hub.ifchange.com/data_group/data_engine:latest` 需要使用的镜像
   `python main.py` 应该执行命名