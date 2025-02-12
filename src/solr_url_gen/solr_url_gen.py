# SPDX-FileCopyrightText: 2025-present Bogatyrev Aleksandr <bogatirevas.dev@gmail.com>

"""
Url generator for solr
"""

from typing import TypedDict, Unpack, Sequence, Mapping, Literal


CH_ASSIGN = "%3A"  # ":"
CH_GLB_LST_SEP = "%2C"  # " "
CH_LST_SEP = "+"
CH_LST_BKT_O = "("
CH_LST_BKT_C = ")"


class _ArgTemplate:
    root = str
    query = str
    result_format = Literal["json", "xml", "python", "ruby", "php", "csv"]
    indent = bool
    fields = Sequence[str]
    filters = Mapping[str, str | Sequence[str]]
    sorts = Mapping[str, Literal["asc", "desc"]]
    group = Mapping[Literal["field", "limit", "sort"], str | int | Mapping[str, Literal["asc", "desc"]]]
    start = int
    rows = int


class _InitKwargs(TypedDict, total=False):
    root: _ArgTemplate.root
    query: _ArgTemplate.query
    result_format: _ArgTemplate.result_format
    indent: _ArgTemplate.indent
    fields: _ArgTemplate.fields
    filters: _ArgTemplate.filters
    sorts: _ArgTemplate.sorts
    group: _ArgTemplate.group
    start: _ArgTemplate.start
    rows: _ArgTemplate.rows


class SolrUrlGenConfig:
    should_update_filters: bool = True
    valid_result_formats: list[str] = ("json", "xml", "python", "ruby", "php", "csv")


class SolrUrlGen:
    def __init__(
        self,
        root: _ArgTemplate.root,
        query: _ArgTemplate.query = "*:*",
        result_format: _ArgTemplate.result_format = "json",
        indent: _ArgTemplate.indent = True,
        fields: _ArgTemplate.fields = None,
        filters: _ArgTemplate.filters = None,
        sorts: _ArgTemplate.sorts = None,
        group: _ArgTemplate.group = None,
        start: _ArgTemplate.start = None,
        rows: _ArgTemplate.rows = None,
    ):
        self._actions = {
            "root": self._set_root,
            "query": self._set_query,
            "result_format": self._set_result_format,
            "indent": self._set_param,
            "fields": self._set_fields,
            "filters": self._set_filters,
            "sorts": self._set_sorts,
            "group": self._set_group,
            "start": self._set_param,
            "rows": self._set_param,
        }
        temp_kwargs = {
            "fields": fields,
            "filters": filters,
            "sorts": sorts,
            "group": group,
            "start": start,
            "rows": rows,
        }
        kwargs = {
            "query": query,
            "result_format": result_format,
            "indent": indent,
        }
        for k, v in temp_kwargs.items():
            if v is not None:
                kwargs[k] = v
        self._conf = SolrUrlGenConfig()
        self._root = root
        self._url = ""
        self._p = {}
        self.get_url(should_update_url=True, **kwargs)

    @property
    def root(self):
        return self._root

    @property
    def url(self):
        return self._url

    @property
    def url_len(self):
        return len(self.url)

    @property
    def should_update_filters(self):
        return self._conf.should_update_filters

    @property
    def valid_result_formats(self):
        return self._conf.valid_result_formats

    def _set_root(self, root):
        self._root = root
        return self.root

    def _set_query(self, query):
        self._p["query"] = query if query not in ["", None] else "*:*"
        self._p["query_str"] = f"?q={query}"
        return self._p["query_str"]

    def _set_result_format(self, result_format):
        rf = result_format if result_format in self.valid_result_formats else "json"
        self._p["result_format"] = rf
        self._p["result_format_str"] = f"&wt={rf}"
        return self._p["result_format_str"]

    def _set_fields(self, fields):
        if fields is None:
            fields = []
        self._p["fields"] = fields
        self._p["fields_str"] = ""
        if len(self._p["fields"]) > 0:
            self._p["fields_str"] = f'{CH_GLB_LST_SEP}'.join(self._p["fields"])
            self._p["fields_str"] = f'&fl={self._p["fields_str"]}'
        return self._p["fields_str"]

    def _set_filters(self, filters):
        if filters is None:
            filters = {}
        should_update = self.should_update_filters
        if should_update and ((len(filters) == 0) or (self._p.get("filters") is None)):
            should_update = False
        if should_update:
            self._p["filters"].update(filters)
        else:
            self._p["filters"] = filters
        self._p["filters_str"] = ""
        if len(self._p["filters"]) > 0:
            for key, value in self._p["filters"].items():
                if isinstance(value, list):
                    filters_str = f'{CH_LST_SEP}'.join(value)
                    self._p[
                        "filters_str"] = f'{self._p["filters_str"]}&fq={key}{CH_ASSIGN}{CH_LST_BKT_O}{filters_str}{CH_LST_BKT_C}'
                else:
                    self._p["filters_str"] = f'{self._p["filters_str"]}&fq={key}{CH_ASSIGN}{value}'
        return self._p["filters_str"]

    def _set_sorts(self, sorts):
        if sorts is None:
            sorts = {}
        self._p["sorts"] = sorts
        self._p["sorts_str"] = ""
        if len(self._p["sorts"]) > 0:
            sorts_str_list = []
            for key, value in self._p["sorts"].items():
                sorts_str_list.append(f'{key}{CH_LST_SEP}{value}')
            self._p["sorts_str"] = f'{CH_GLB_LST_SEP}'.join(sorts_str_list)
            self._p["sorts_str"] = f'&sort={self._p["sorts_str"]}'
        return self._p["sorts_str"]

    def _set_group(self, group):
        if group is None:
            group = {}
        self._p["group"] = group
        self._p["group_str"] = ""
        if (len(group) > 0) and (group.get("field") is not None):
            self._p["group_str"] = f'&group=true&group.ngroups=true&group.field={group["field"]}'
            if group.get("limit") is not None:
                self._p["group_str"] = f'{self._p["group_str"]}&group.limit={group["limit"]}'
            if (group.get("sort") is not None) and (len(group["sort"]) > 0):
                sorts_str_list = []
                for key, value in group["sort"].items():
                    sorts_str_list.append(f'{key}{CH_LST_SEP}{value}')
                sorts_str = f'{CH_GLB_LST_SEP}'.join(sorts_str_list)
                self._p["group_str"] = f'{self._p["group_str"]}&group.sort={sorts_str}'
        return self._p["group_str"]

    def _set_param(self, value, key):
        key_str = f"{key}_str"
        if value is None:
            value = ""
        self._p[key] = value
        self._p[key_str] = ""
        if value != "":
            self._p[key_str] = f"&{key}={value}"
        return self._p[key_str]

    def _update_url(self):
        self._url = self.root
        for key in self._actions.keys():
            value = self._p.get(f"{key}_str")
            if value not in ["", None]:
                self._url = f"{self.url}{value}"
        return self.url

    def get_url(self, should_update_url=False, **kwargs: Unpack[_InitKwargs]):
        """
        :param should_update_url: if false it will update the URL only when changes are detected in kwargs,
            otherwise it will generate it again (can be useful if some parts of the URL are changed by illegal methods)
        :return: generated url
        """
        for key, value in kwargs.items():
            action = self._actions.get(key)
            if action is not None:
                should_update_url = True
                params = [value]
                if action.__name__ == "_set_param":
                    params.append(key)
                action(*params)
        if should_update_url:
            self._update_url()
        return self.url

    def switch_update_filters(self):
        """
        By default, when setting filters in get_url, they are updated based on the passed keys
        instead of completely rewriting

        :return: established value
        """
        self._conf.should_update_filters = not self.should_update_filters
        return self.should_update_filters

    def print_params(self):
        print(f"root: {self.root}")
        for key, value in self._p.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    HOST = "host"
    PORT = "port"
    COLLECTION = "collection"
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
    group_field_values = ["1", "2", "3"]
    result_url = sug.get_url(filters={"group_field": group_field_values})
    print(result_url)
    sug.print_params()
