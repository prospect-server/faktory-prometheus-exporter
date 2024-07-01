"""Basic Faktory metrics exporter for Prometheus.

Output example of the Faktory info call.
{'faktory': {
  'queues': {'default': 0, 'etl': 0, 'grafana-preview': 0},
  'tasks': {
    'Busy': {'reaped': 15, 'size': 0},
    'Dead': {'cycles': 1013, 'enqueued': 0, 'size': 8, 'wall_time_sec': 0.235679883},
    'Retries': {'cycles': 12129, 'enqueued': 39, 'size': 0, 'wall_time_sec': 2.258407141},
    'Scheduled': {'cycles': 12129, 'enqueued': 0, 'size': 0, 'wall_time_sec': 6.048978778},
    'Workers': {'reaped': 0, 'size': 2}},
  'total_enqueued': 0, 'total_failures': 116, 'total_processed': 2331, 'total_queues': 3
},
'now': '2024-06-24T10:59:14.856756798Z',
'server': {
  'command_count': 156157, 'connections': 10, 'description': 'Faktory',
  'faktory_version': '1.8.0', 'uptime': 60649, 'used_memory_mb': 13},
'server_utc_time': '10:59:14 UTC'}
"""  # noqa: E501

import time

import click
from prometheus_client import Gauge, Summary, generate_latest, start_http_server
from pyfaktory import Client

INTERVAL_IN_SECONDS = 30
# Create a metric to track time spent and requests made.
scraping_time = Summary("exporter_scraping_seconds", "Time spent scraping metrics")
command_count = Gauge("command_count", "Faktory Command Count")
connections = Gauge("connections", "Connections count")
jobs = Gauge("jobs", "Faktory Jobs count", ["state"])
total_queues = Gauge("total_queues", "Faktory queues")
enqueued_per_queue = Gauge("enqueued_per_queue", "Jobs enqueued in queues", ["name"])
retries_enqueued = Gauge("retries_enqueued", "Job retries enqueued")
dead_size = Gauge("dead_size", "Job Dead")

@scraping_time.time()
def scrape_info(faktory_url: str) -> dict:
    """Scraping."""
    with Client(faktory_url=faktory_url) as client:
        info = client.info()
    return info


def process(faktory_url: str) -> None:
    """Gather the important information in Prometheus Metrics."""
    info = scrape_info(faktory_url=faktory_url)
    command_count.set(info["server"]["command_count"])
    connections.set(info["server"]["connections"])
    jobs.labels("enqueued").set(info["faktory"]["total_enqueued"])
    jobs.labels("failures").set(info["faktory"]["total_failures"])
    jobs.labels("processed").set(info["faktory"]["total_processed"])
    total_queues.set(info["faktory"]["total_queues"])
    for name, size in info["faktory"]["queues"].items():
        enqueued_per_queue.labels(name).set(size)
    retries_enqueued.set(info["faktory"]["tasks"]["Retries"]["enqueued"])
    dead_size.set(info["faktory"]["tasks"]["Dead"]["size"])


def _run_interactive(faktory_url: str) -> None:
    process(faktory_url=faktory_url)
    print(generate_latest().decode(), end="")  # noqa: T201


def _run_daemonize(faktory_url: str, port: int) -> None:
    print(f"Running on port {port}, you may check http://localhost:{port}/metrics")  # noqa: T201
    start_http_server(port)

    while True:
        process(faktory_url=faktory_url)
        time.sleep(INTERVAL_IN_SECONDS)


@click.command()
@click.option(
    "--faktory_url",
    envvar="FAKTORY_URL",
    default="tcp://:@localhost:7419",
    help="Faktory server URL.",
)
@click.option(
    "--daemonize", "-d",
    envvar="DAEMONIZE_EXPORTER",
    is_flag=True,
    default=False,
    help="Daemonize exporter.",
)
@click.option(
    "--port", "-p",
    envvar="PORT",
    default=7423,
    help="Port to run the daemon, makes only sense with the --daemon option.",
)
def main(faktory_url: str, daemonize: bool, port: int) -> None:
    """Basic Faktory metrics exporter for Prometheus."""
    if daemonize:
        _run_daemonize(faktory_url=faktory_url, port=port)
    else:
        _run_interactive(faktory_url=faktory_url)


if __name__ == "__main__":
    main()
