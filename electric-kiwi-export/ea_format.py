"""
Basic writer of Electricity Authority EIEP13A format
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, TextIO


DATETIME_FORMAT = '%d/%m/%Y %H:%M:%S'

@dataclass
class EaHeader:
    sending_party: str
    """Name of sending party."""

    participant_identifier: str
            
    start_date: datetime
    """Report run start date (inclusive)"""

    end_date: datetime
    """Report run end date (inclusive)"""

    hdr: Literal['HDR'] = 'HDR'
    """indicates the row is a header record type"""
    
    icpcons: Literal['ICPCONS'] = 'ICPCONS'
    """Must be ICPCONS."""

    version: float = 1.4
    """Version of EIEP that is being used for this file."""

    recipient_id: str = 'CUST'
    
    run_date: datetime = datetime.now()
    """Date the report is run"""

    request_id: str = ''
    """The unique request identifier"""

@dataclass
class EaRecord:
    consumer_authorisation_code: str
    icp_identifier: str
    metering_component_serial_number: str
    period_of_availability: int
    read_period_start: datetime
    read_period_end: datetime
    unit_quantity: float
    register_content_code: str = 'IN'
    response_code: Literal['000'] = '000'
    unit_quantity_reactive: float | Literal[''] = ''
    read_status: Literal['RD'] | Literal['ES'] = 'RD'
    energy_flow_direction: Literal['I'] | Literal['X'] = 'X'
    nzdt_adjustment: Literal[''] | Literal['NZST'] = 'NZST'
    detail_record_type: Literal['DET'] = 'DET'


class EaFile:

    _header: EaHeader
    _records: list[EaRecord] = []

    def __init__(self, f: TextIO):
        self._f = f

    def __enter__(self):
        return self

    def write_header(self, h: EaHeader):
        # The header can't be written until the end because it contains the number of records
        self._header = h
    
    def write_record(self, r: EaRecord):
        self._records.append(r)
    
    def _actually_write_header(self):
        h = self._header
        self._f.write(','.join([
            h.hdr,
            h.icpcons,
            str(h.version),
            h.sending_party,
            h.participant_identifier,
            h.recipient_id,
            h.run_date.strftime(DATETIME_FORMAT),
            h.request_id,
            str(len(self._records)),
            h.start_date.strftime(DATETIME_FORMAT),
            h.end_date.strftime(DATETIME_FORMAT),
        ]) + '\n')
    
    def _actually_write_record(self, record: EaRecord):
        r = record
        self._f.write(','.join([
            r.detail_record_type,
            r.consumer_authorisation_code,
            r.icp_identifier,
            r.response_code,
            r.nzdt_adjustment,
            r.metering_component_serial_number,
            r.energy_flow_direction,
            r.register_content_code,
            str(r.period_of_availability),
            r.read_period_start.strftime(DATETIME_FORMAT),
            r.read_period_end.strftime(DATETIME_FORMAT),
            r.read_status,
            str(r.unit_quantity),
            str(r.unit_quantity_reactive),
        ]) + '\n')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._actually_write_header()
        for r in self._records:
            self._actually_write_record(r)
