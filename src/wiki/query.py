import web
from .wiki_error import WikiError
from .constants import COMMA, Field, Table
from .order_by import OrderBy
from .where import Where

_API_URL = "https://www.poewiki.net/w/api.php?action=cargoquery&format=json&tables={0}&fields={1}&where={2}&group_by={3}&order_by={4}&join_on={5}&limit={6}"
_PHP_URL = "https://www.poewiki.net/index.php?title=Special:CargoExport&format=json&tables={0}&fields={1}&where={2}&order+by={4}&join+on={5}&limit={6}"

_NO_TABLES_ERROR = "No tables were provided to query the wiki with."
_NO_FIELDS_ERROR = "No fields were provided to query the wiki with."
_NO_JOIN_FOR_MULTITABLE_ERROR = "No join_on parameter provided for a query involving these tables: {0}."
_JOIN_FOR_ONE_TABLE_ERROR = "Provided a join_on parameter '{0}' to query a single table '{1}'."
_OUT_OF_RANGE_LIMIT_ERROR = "Provided an out-of-range 'limit' parameter: '{0}'. The value must be between 1 and 500."

class Query:
    """Represents a Wiki database query."""
    def __init__(self, tables: Table | list[Table], fields: Field | list[Field], join_on: Field = Field.NONE):
        """
        * `tables`: the table or tables to query.
        * `fields`: the field or fields to obtain from the tables queried.
        * `join_on`: the table fields to join on in case of multiple tables being queried.
        Mandatory for multi-table queries. 
        """
        tables = [ tables ] if type(tables) == Table else tables
        if len(tables) == 0:
            raise WikiError(_NO_TABLES_ERROR)
        if len(tables) > 1 and join_on == Field.NONE:
            raise WikiError(_NO_JOIN_FOR_MULTITABLE_ERROR.format(str(tables)))
        if len(tables) == 1 and join_on != Field.NONE:
            raise WikiError(_JOIN_FOR_ONE_TABLE_ERROR.format(join_on.value, str(tables)))
        
        fields = [ fields ] if type(fields) == Field else fields
        if len(fields) == 0:
            raise WikiError(_NO_FIELDS_ERROR)
        
        self._tables: list[Table] = tables
        self._fields: list[Table] = fields
        self._join_on = join_on
        self._where = None
        self._group_by = Field.NONE
        self._order_by = OrderBy()
        self._limit = 500

    def where(self, where: Where):
        """Sets the `where` clause to use during querying."""
        self._where = where
        return self
    
    def group_by(self, group_by: Field):
        """Sets the `group_by` field to use during querying."""
        self._group_by = group_by
        return self
    
    def order_by(self, order_by: OrderBy):
        """Sets the `order_by` clause to use during querying."""
        self._order_by = order_by
        return self
    
    def limit(self, limit: int):
        """Sets the limit of results to obtain from querying.
        An error raised if the value is less than 1 or more than 500.
        Default is 500."""
        if limit > 500 or limit < 1:
            raise WikiError(_OUT_OF_RANGE_LIMIT_ERROR.format(str(limit)))
        self._limit = limit
        return self

    def run(self):
        """Executes the query and returns a list with the results."""
        records = web.get(self._get_query_string())
        return [ _remove_whitespace_in_keys(record) for record in records ]
    
    def _get_query_string(self):
        tables = COMMA.join([ table.value for table in self._tables ])
        fields = COMMA.join([ field.value for field in self._fields ])
        where = str(self._where) if self._where != None else ""
        return _PHP_URL.format(tables, fields, where, self._group_by.value, str(self._order_by), self._join_on.value, str(self._limit))
    
def _remove_whitespace_in_keys(dictionary: dict[str]):
    new_dictionary = {}
    for key in dictionary:
        new_dictionary[key.replace(" ", "_")] = dictionary[key]
    return new_dictionary