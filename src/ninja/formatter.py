import repoe
from dataclasses import dataclass
from core import Sieve
from .constants import QueryType, Field, Record, RecordsJSON
from .value_range import ValueRange
from .utils import BaseTypeGetter, ValueGetter, Validator

import json

@dataclass
class Formatter:
    _url: str
    _base_type_getter: BaseTypeGetter
    _value_getter: ValueGetter
    _validator: Validator

    def get_url(self, query_type: QueryType, league_name: str):
        return self._url.format(league_name, query_type)
    
    def validate(self, record: Record, range: ValueRange, sieve: Sieve):
        return self._validator(record, range, sieve)

    def __call__(self, records_json: RecordsJSON):
        return [ self._get_formatted_record(record, records_json) 
            for record in records_json[Field.LINES] ]

    def _get_formatted_record(self, record: Record, records_json: RecordsJSON):
        record[Field.CHAOS_VALUE] = self._value_getter(record)
        record[Field.BASE_TYPE] = self._base_type_getter(record, records_json)
        record[Field.CLASS] = repoe.get_class_for_base(record[Field.BASE_TYPE])
        return record