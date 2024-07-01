FROM python:3.12-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Uncomment the following lines to make it run locally, also without git
# WORKDIR /code/
# ENV SETUPTOOLS_SCM_PRETEND_VERSION v0.0.0
# COPY requirements.txt .
# RUN pip install -r requirements.txt
# COPY . .
# RUN pip install .

# If ran locally, comment this line out
RUN pip install faktory_prometheus_exporter

EXPOSE     7423
ENTRYPOINT [ "faktory-prometheus-exporter" ]
