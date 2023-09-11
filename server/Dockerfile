#Author: Peter Gutstein
FROM python:latest

ADD server/server.py /server/
COPY generalFunctions.py/ /server/

WORKDIR /server/

EXPOSE 54321/udp

ENTRYPOINT ["python3", "-u", "server.py"]
