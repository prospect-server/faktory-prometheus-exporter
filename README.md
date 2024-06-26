# faktory-prometheus-exporter

> A Faktory Exporter written in Python for Prometheus.

---

## In a nutshell

The *faktory_exporter* is a simple server that scrapes a configured 
[Faktory](https://github.com/contribsys/faktory)
instance for stats by issuing the "INFO" command and exports them via string message
for [Prometheus](https://prometheus.io/docs/introduction/overview/) consumption.

## Usage

The URL used to scrape info from faktory is by default `tcp://:@localhost:7419`, but
can be overwritten by using the `--faktory_url` arg or by specifying a `FAKTORY_URL`
environment variable.

### Install with pip

Fastest way is simply running (preferably in a python env):
```
pip install faktory-prometheus-exporter
faktory-prometheus-exporter [--faktory_url='tcp://:[password]@localhost:7419']
```

### Develop using uv or pip-compile

The requirements format are the ones defined by `pip-compile`, from 
[pip-tools](https://github.com/jazzband/pip-tools).
You may also equally use `uv pip compile` from [uv](https://github.com/astral-sh/uv).

```
uv pip compile requirements.in -o requirements.txt
uv pip compile requirements-dev.in -o requirements-dev.txt
```

Then you can either install locally to use the CLI or to run the python function:

```
uv pip install -e .
faktory-prometheus-exporter [--faktory_url='tcp://:[password]@localhost:7419']
python faktory_prometheus_exporter.py
```

### Build and use as docker container

You may use the Dockerfile and run something like the following. Make sure that the
exporter is in the same network than faktory, i.e. with `docker-compose`.

```
docker build -t faktory-prometheus-exporter:latest .
docker run -d [--rm] faktory-prometheus-exporter:latest [--faktory_url='tcp://:[password]@localhost:7419']
```

### Inspiration / prior work

Inspired by [this Faktory Exporter](https://github.com/lukasmalkmus/faktory_exporter/)
written in go, but only partially maintained and not working out of the box when we
needed it, so we built our own one.
