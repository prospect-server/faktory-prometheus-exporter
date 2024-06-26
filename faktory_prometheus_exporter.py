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

import click
from prometheus_client import Gauge, Summary, generate_latest
from pyfaktory import Client

# Create a metric to track time spent and requests made.
scraping_time = Summary("exporter_scraping_seconds", "Time spent scraping metrics")


@scraping_time.time()
def scrape_info(faktory_url: str) -> dict:
    """Scraping."""
    with Client(faktory_url=faktory_url) as client:
        info = client.info()
    return info


def process(faktory_url: str) -> None:
    """Gather the important information in Prometheus Metrics."""
    info = scrape_info(faktory_url=faktory_url)
    c = Gauge("command_count", "Faktory Command Count")
    c.set(info["server"]["command_count"])
    c = Gauge("connections", "Connections count")
    c.set(info["server"]["connections"])
    c = Gauge("jobs", "Faktory Jobs count", ["state"])
    c.labels("enqueued").set(info["faktory"]["total_enqueued"])
    c.labels("failures").set(info["faktory"]["total_failures"])
    c.labels("processed").set(info["faktory"]["total_processed"])
    c = Gauge("total_queues", "Faktory queues")
    c.set(info["faktory"]["total_queues"])
    c = Gauge("enqueued_per_queue", "Jobs enqueued in queues", ["name"])
    for name, size in info["faktory"]["queues"].items():
        c.labels(name).set(size)
    c = Gauge("retries_enqueued", "Job retries enqueued")
    c.set(info["faktory"]["tasks"]["Retries"]["enqueued"])
    c = Gauge("dead_size", "Job Dead")
    c.set(info["faktory"]["tasks"]["Dead"]["size"])


@click.command()
@click.option(
    "--faktory_url",
    envvar="FAKTORY_URL",
    default="tcp://:@localhost:7419",
    help="Faktory server URL.",
)
def main(faktory_url: str) -> None:
    """Basic Faktory metrics exporter for Prometheus."""
    process(faktory_url=faktory_url)
    print(generate_latest().decode(), end="")  # noqa: T201


if __name__ == "__main__":
    main()
