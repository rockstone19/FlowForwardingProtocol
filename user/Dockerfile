#Author: Peter Gutstein
FROM python:latest

ADD user/user.py /user/
COPY generalFunctions.py/ /user/

WORKDIR /user/

EXPOSE 54321/udp

ENTRYPOINT ["python3", "-u", "user.py"]
