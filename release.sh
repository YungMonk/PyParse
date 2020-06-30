#!/bin/bash

set -e

dockerName='data_engine'
VERSION=v$(date "+%Y%m%d%H%M")

git checkout master
git pull
git tag $VERSION
git push origin master --tag

docker build -t hub.ifchange.com/data_group/$dockerName:$VERSION .
docker tag hub.ifchange.com/data_group/$dockerName:$VERSION hub.ifchange.com/data_group/$dockerName:latest
docker push hub.ifchange.com/data_group/$dockerName:$VERSION
docker push hub.ifchange.com/data_group/$dockerName:latest

# 运行容器
docker run --rm -d -it --name=data_engine hub.ifchange.com/data_group/data_engine:latest