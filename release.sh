#!/bin/bash

set -e

dockerName='data_engine'
VERSION=v$(date "+%Y%m%d%H%M")

git checkout master
git pull
git tag $VERSION
git push origin master --tag

docker build -t hub.ifchange.com/data_group/$dockerName:$VERSION .
docker tag hub.ifchange.com/data_group/$dockerName:$VERSION docker.ifchange.com/data_group/$dockerName:latest
docker push hub.ifchange.com/data_group/$dockerName:$VERSION
docker push hub.ifchange.com/data_group/$dockerName:latest