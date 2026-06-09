import repoe
from dataclasses import dataclass
from core import Sieve
from .constants import Field, Record, RecordsJSON
from .value_range import ValueRange
from .utils import TargetGetter, ValueGetter, Validator

@dataclass
class Formatter:
    _url: str
    _target_getter: TargetGetter
    _value_getter: ValueGetter
    _validator: Validator

    def get_url(self, target: str, league_name: str):
        return self._url.format(league_name, target)

    def validate(self, record: Record, range: ValueRange, sieve: Sieve):
        return self._validator(record, range, sieve)

    def __call__(self, records_json: RecordsJSON):
        return [ self._get_formatted_record(record, records_json)
            for record in records_json[Field.LINES] ]

    def _get_formatted_record(self, record: Record, records_json: RecordsJSON):
        if Field.BASE_TYPE in record:
            record[Field.CLASS] = repoe.get_class_for_base(record[Field.BASE_TYPE])

        record[Field.CHAOS_VALUE] = self._value_getter(record)
        record[Field.TARGET] = self._target_getter(record, records_json)
        return record