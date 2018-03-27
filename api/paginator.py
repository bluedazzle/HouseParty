# coding: utf-8
from __future__ import unicode_literals

from django.core.paginator import Paginator


class SearchPaginator(Paginator):
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True, *args, **kwargs):
        super(SearchPaginator, self).__init__(object_list, per_page, orphans, allow_empty_first_page)

    def _get_count(self):
        """
        Returns the total number of objects, across all pages.
        """
        return 450000

    count = property(_get_count)
