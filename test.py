import json
import src.wiki.queries as queries

result = queries.get_uniques([ "Daggers", "Claws" ])
print(json.dumps(result, indent=2))