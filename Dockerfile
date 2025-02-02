FROM python:3.9-slim
WORKDIR /code
ENV REDIS_HOST=172.17.0.1
ENV REDIS_PORT=6379
RUN apt-get install tzdata
ENV TZ America/Curacao
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app/"]