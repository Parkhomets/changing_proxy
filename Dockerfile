FROM ubuntu:20.04

LABEL \
    name="TOR HTTP Proxy" \
    author="Pavel Parkhomets (@gremlin_97)" \
    description="HTTP proxy via TOR network - switch IP every 10 second (based on torghost)" 

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /root/
COPY main.sh .
RUN chmod +x main.sh

COPY torghost .
COPY squid.conf /etc/squid/squid.conf

RUN apt -qq update -y && \
    apt -qq install -y  --no-install-recommends squid && \
    apt -qq install -y tor sudo python3 python3-pip iptables && \
    pip3 -q install -r requirements.txt packaging

EXPOSE 5000

CMD ["./main.sh"]