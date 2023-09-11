#Author: Peter Gutstein

FROM python:latest

ADD controller/controller.py /controller/
COPY generalFunctions.py/ /controller/

WORKDIR /controller/

EXPOSE 54321/udp

ENTRYPOINT ["python3", "-u", "controller.py"]
