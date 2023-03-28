FROM alpine:3.14
MAINTAINER xxiaokexiang@gmail.com
RUN mkdir -p /root/tfoled \
    && echo -e "nameserver 114.114.114.114\n nameserver 223.5.5.5" > /etc/hosts \ 
    && sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
RUN apk update && apk add python3 py3-pip net-tools python3-dev bc linux-headers gcc g++ libxslt-dev openssl-dev jpeg-dev zlib-dev
WORKDIR /root/tfoled
COPY . /root/tfoled/
RUN pip3 config set global.index-url http://pypi.douban.com/simple/ && pip3 config set global.trusted-host pypi.douban.com
RUN python3 setup.py install && pip3 install -r requirements.txt
ENTRYPOINT ["python3", "/root/tfoled/TFOL.py", "&"]
