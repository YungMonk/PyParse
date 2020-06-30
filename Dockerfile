FROM python:3.8.2-slim

WORKDIR /opt/www/data_engine

COPY  ./ /opt/www/data_engine

VOLUME /opt/log/data_engine

RUN pip install -r /opt/www/data_engine/requirements.txt -i https://pypi.douban.com/simple

CMD ["python", "index.py"]