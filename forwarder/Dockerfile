#Author: Peter Gutstein
FROM python:latest

ADD forwarder/forwarder.py /forwarder/
COPY generalFunctions.py/ /forwarder/

WORKDIR /forwarder/

EXPOSE 54321/udp

ENTRYPOINT ["python3", "-u", "forwarder.py"]
