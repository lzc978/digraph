FROM python:3.6.8 as frontend

#标记 开发为 eaon 及 邮箱
LABEL maintainer="braveheart<lzc978@126.com>"
COPY --from=frontend ../* /app
WORKDIR /app/digraph
RUN pip install -U -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && mkdir -p ./logs \
    && mkdir -p ./model \
    && mkdir -p ./model/correct \
    && chmod -R 764 ./model

#FROM mysql:1 as fo
#FROM nginx:v2

#CMD ["/bin/bash", "dg_test.sh"]
