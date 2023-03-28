FROM ubuntu:22.04
RUN echo -e "nameserver 114.114.114.114\n nameserver 223.5.5.5" > /etc/hosts
RUN apt update \
    && apt install python3 -y \ 
    && apt install python3-pip -y \ 
    && apt install net-tools -y \ 
    && apt install vim -y \ 
    && apt install bc -y \
    && mkdir -p /root/tfoled 
WORKDIR /root/tfoled
COPY . /root/tfoled/
RUN pip3 config set global.index-url http://pypi.douban.com/simple/ && pip3 config set global.trusted-host pypi.douban.com
RUN python3 setup.py install && pip3 install -r requirements.txt
ENTRYPOINT ["python3", "/root/tfoled/TFOL.py", "&"]

