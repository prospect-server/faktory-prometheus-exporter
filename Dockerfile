FROM python:3.12-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# WORKDIR /code/

# COPY requirements.txt .
# RUN pip install -r requirements.txt

# COPY . .
# RUN pip install .

RUN pip install faktory_prometheus_exporter

ENTRYPOINT [ "faktory-prometheus-exporter" ]
