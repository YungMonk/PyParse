#!/bin/bash

set -e

dockerName='data_engine'
VERSION=v$(date "+%Y%m%d%H%M")

# 使用最新的代码构建
# git checkout master
# git pull

# 创建版本的节点
# git tag $VERSION
# git push origin master --tag

# 构建容器
docker build -t hub.ifchange.com/data_group/$dockerName:$VERSION .
docker tag hub.ifchange.com/data_group/$dockerName:$VERSION hub.ifchange.com/data_group/$dockerName:latest

# 推送到远程
# docker push hub.ifchange.com/data_group/$dockerName:$VERSION
# docker push hub.ifchange.com/data_group/$dockerName:latest