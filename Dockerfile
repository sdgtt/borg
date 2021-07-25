FROM python:3.8

RUN pip install fastapi uvicorn

# REST
EXPOSE 6000
# NFS
EXPOSE 111
EXPOSE 2049
EXPOSE 1048
# TFTP
EXPOSE 69

# Setup
RUN ["mkdir", "/setup"]
COPY ./borg /borg
COPY setup.sh /setup/setup.sh
COPY runtime.sh /setup/runtime.sh
RUN ["chmod", "+x", "/setup/setup.sh"]
RUN ["chmod", "+x", "/setup/runtime.sh"]

CMD ["bash", "/setup/runtime.sh"]

