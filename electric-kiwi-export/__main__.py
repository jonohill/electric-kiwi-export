# pyright: strict
# pyright: reportUnknownMemberType=false

import argparse
import logging
from datetime import datetime, timedelta
from os import environ
from sys import stdout
from typing import TypedDict
from zoneinfo import ZoneInfo

import arrow
from dotenv import load_dotenv  # type: ignore

from .ea_format import EaFile, EaHeader, EaRecord
from .electrickiwi.electrickiwi import ElectricKiwi

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

load_dotenv()
USERNAME = environ.get("EK_USERNAME")
PASSWORD = environ.get("EK_PASSWORD")

if not USERNAME or not PASSWORD:
    raise Exception("Set the environment variables EK_USERNAME and EK_PASSWORD")


parser = argparse.ArgumentParser(prog='electric-kiwi-export')
parser.add_argument("--start", help="Start date", type=datetime.fromisoformat, default=datetime.now() - timedelta(days=7))
parser.add_argument("--end", help="End date", type=datetime.fromisoformat, default=datetime.now())
args = parser.parse_args()


TIME_FORMAT = '%I:%M %p'
OUT_DATE_FORMAT = '%d/%m/%Y'
TZ = ZoneInfo('Pacific/Auckland')

class Connection(TypedDict):
    icp_identifier: str

class IntervalConsumption(TypedDict):
    consumption: str
    time: str

class DayConsumption(TypedDict):
    intervals: dict[str, IntervalConsumption]


ek = ElectricKiwi()

token: str = ek.at_token()
hashed = ek.password_hash(PASSWORD)
ek.login(USERNAME, hashed)

connection = ek.connection_details()

# Request max 7 days as a time
days_written: set[str] = set()

with EaFile(stdout) as f:

    f.write_header(EaHeader(
        sending_party='ELKI',
        participant_identifier='ELKI',
        start_date=args.start,
        end_date=args.end,
    ))

    start = args.start.astimezone(TZ)
    very_end = args.end.astimezone(TZ)
    while True:
        end = min(start + timedelta(days=7), very_end)

        data: dict[str, DayConsumption] = ek.consumption(
            arrow.Arrow.fromdatetime(start),
            arrow.Arrow.fromdatetime(end),
        )
        items = sorted(data.items())
        for day, values in items:
            log.info(f"{day}")

            if day in days_written:
                continue

            day_date = datetime.fromisoformat(day)

            intervals = values['intervals']
            for n in range(1, 49):
                k = str(n)
                if k not in intervals:
                    continue

                start_time = datetime.strptime(intervals[k]['time'], TIME_FORMAT)
                end_time = start_time + timedelta(minutes=30)
                start = datetime.combine(day_date, start_time.time(), TZ)
                end = datetime.combine(day_date, end_time.time(), TZ)

                f.write_record(EaRecord(
                    consumer_authorisation_code='',
                    icp_identifier=connection['icp_identifier'],
                    metering_component_serial_number='',
                    period_of_availability=30,
                    read_period_start=start,
                    read_period_end=end,
                    unit_quantity=float(intervals[k]['consumption']),
                    nzdt_adjustment='' if end.dst() else 'NZST',
                ))

            days_written.add(day)
        

        if end >= very_end:
            break
        start = end
