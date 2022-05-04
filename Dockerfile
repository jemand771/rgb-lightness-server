FROM python:3

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        libsm6 \
        libxext6 \
    && \
    apt-get clean

RUN mkdir -p /tmp
WORKDIR /tmp
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir -p /app
WORKDIR /app
COPY main.py .
COPY templates ./templates

CMD ["gunicorn", "--bind", "0.0.0.0:80", "main:app"]
