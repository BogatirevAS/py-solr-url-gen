# Solr Url Generator

Url generator for solr

-----

## Table of Contents

- [Installation](#installation)
- [Examples](#examples)

## Installation

- console
```console
pip install git+https://github.com/BogatirevAS/py-solr-url-gen.git@master
```
```console
pip install git+https://github.com/BogatirevAS/py-solr-url-gen.git@0.3.0
```

- requirements.txt
```requirements
solr-url-gen @ git+https://github.com/BogatirevAS/py-solr-url-gen.git@master
```
```requirements
solr-url-gen @ git+https://github.com/BogatirevAS/py-solr-url-gen.git@0.3.0
```

## Examples

```python
from solr_url_gen import SolrUrlGen


HOST = "host"
PORT = "port"
COLLECTION = "collection"

# initialization of the main body of url
sug = SolrUrlGen(
    root=f"http://{HOST}:{PORT}/solr/{COLLECTION}/select",
    result_format="json",
    fields=["field_value", "field_date"],
    filters={"filter_field": "filter_field_value"},
    sorts={"group_field": "asc"},
    group={"field": "group_field", "limit": 3, "sort": {"field_date": "desc"}},
    start=0,
    rows=10,
)

# set dinamic filters
group_field_values = ["1", "2", "3"]
url = sug.get_url(filters={"group_field": group_field_values})
```

```python
# generated url
print(url)
# http://host:port/solr/collection/select?q=*:*&wt=python&indent=True
# &fl=field_value%2Cfield_date&fq=filter_field%3Afilter_field_value&fq=group_field%3A(1+2+3)&sort=group_field+asc
# &group=true&group.ngroups=true&group.field=group_field&group.limit=3&group.sort=field_date+desc&start=0&rows=10

# check internal parameters
sug.print_params()
# root: http://host:port/solr/collection/select
# query: *:*
# query_str: ?q=*:*
# result_format: json
# result_format_str: &wt=json
# indent: True
# indent_str: &indent=True
# fields: ['field_value', 'field_date']
# fields_str: &fl=field_value%2Cfield_date
# filters: {'filter_field': 'filter_field_value', 'group_field': ['1', '2', '3']}
# filters_str: &fq=filter_field%3Afilter_field_value&fq=group_field%3A(1+2+3)
# sorts: {'group_field': 'asc'}
# sorts_str: &sort=group_field+asc
# group: {'field': 'group_field', 'limit': 3, 'sort': {'field_date': 'desc'}}
# group_str: &group=true&group.ngroups=true&group.field=group_field&group.limit=3&group.sort=field_date+desc
# start: 0
# start_str: &start=0
# rows: 10
# rows_str: &rows=10
```

```python
# simple use
import requests


r = requests.get(url)
if r.ok:
    res = r.json()
    print(res)
```
