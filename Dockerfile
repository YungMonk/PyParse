FROM python:3.8.2-slim


RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak  
COPY sources.list /etc/apt/sources.list

RUN apt-get update \
&& apt-get install -y curl \
&& apt-get install -y libcurl4-gnutls-dev \
&& apt-get install -y libghc-gnutls-dev

WORKDIR /opt/www/data_engine

COPY  ./ /opt/www/data_engine

RUN pip install -r /opt/www/data_engine/requirements.txt -i https://pypi.douban.com/simple

CMD ["python", "index.py"]