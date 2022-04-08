# first stage
FROM python:3.8-slim

RUN apt update && \
    apt install --no-install-recommends -y build-essential gcc && \
    apt clean && rm -rf /var/lib/apt/lists/*
COPY ./requirements.txt /requirements.txt
COPY ./server /server


RUN pip3 install --no-cache-dir --user -r requirements.txt

EXPOSE 80
EXPOSE 443

# make sure you include the -u flag to have our stdout logged
CMD ["python","-u", "server/server.py"]
#     "--certfile", "/etc/letsencrypt/live/fatsolko.xyz/cert.pem",\
#     "--keyfile", "/etc/letsencrypt/live/fatsolko.xyz/privkey.pem", "app:app"]



