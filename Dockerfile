FROM python:3.10-slim

ENV IN_DOCKER=true

RUN apt-get update && apt-get install -y tar \
    && apt-get clean

WORKDIR /app

COPY . /app

RUN chmod +x /app/scripts/setup_docker.sh /app/scripts/run.sh

RUN /app/scripts/setup_docker.sh

RUN mkdir -p /app/chroma_db && \
    tar -xzf /app/chroma_db_backup.tar.gz -C /app/chroma_db --strip-components=1 && \
    rm /app/chroma_db_backup.tar.gz

EXPOSE 8000

CMD ["/app/scripts/run.sh"]
