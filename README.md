# Parse Engine


> Parse_Engine 是一个`Web`网页内容的数据分析应用，主要功能是对从网页上采集的数据进行分析，格式化。使数据内容转化为更为方便其它应用使用的 `json` 数据内容


#### 应用docker镜像

> 在项目目录下执行 `./release.sh` ，拉取最新代码，生成docker镜像，并上传镜像到远程仓库


#### 启动docker容器

```shell
docker run --rm -it -p 8880:8880 \
-v /opt/log/data_engine:/opt/log/data_engine \
--add-host dev.gsystem.rpc:192.168.1.66 \
--name=data_engine \
hub.ifchange.com/data_group/data_engine:latest python index.py
```
> 执行命令解说：
   `-v /opt/log/data_engine:/opt/log/data_engine` 将容器内的日志文件，映射到时宿主机；
   `--add-host dev.gsystem.rpc:192.168.1.66` 将需要用到的第三方服务的域名映射到时其主机；
   `--name=data_engine` 设置容器名；
   `hub.ifchange.com/data_group/data_engine:latest` 需要使用的镜像
   `python index.py` 应该执行命名