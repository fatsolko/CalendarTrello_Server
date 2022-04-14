# first stage
FROM python:3.8-slim

RUN apt update \
    && apt install --no-install-recommends -y build-essential gcc \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir --user -r ./requirements.txt

COPY ./server /server


EXPOSE 80 443

# include the -u flag to have our stdout logged
CMD ["python","-u", "server/server.py"]




