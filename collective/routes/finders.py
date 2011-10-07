from Products.CMFCore.utils import getToolByName
from datetime import datetime
from DateTime import DateTime
import calendar

_non_list_keys = ('sort_on', 'sort_order', 'sort_limit')


def _normalizeQuery(query):
    dates = {}
    for key, value in query.items():
        if '__' in key:
            name, _type = key.split('__')
            if name not in dates:
                dates[name] = {}
            dates[name][_type] = value
            del query[key]
        else:
            if type(value) not in (list, tuple, set):
                if key not in _non_list_keys:
                    query[key] = [value]
            else:
                query[key] = list(value)
    now = datetime.utcnow()
    for key, value in dates.items():
        if 'year' in value:
            year = (value['year'], value['year'])
        else:
            year = (1901, now.year)
        if 'month' in value:
            month = (value['month'], value['month'])
        else:
            month = (1, 12)
        if 'day' in value:
            day = (value['day'], value['day'])
        else:
            day = (1, calendar.monthrange(year[1], month[1])[1])
        sd = DateTime(year[0], month[0], day[0], 0, 0, 0)
        ed = DateTime(year[1], month[1], day[1], 23, 59, 59)
        query[key] = {'query': [sd, ed], 'range': 'min:max'}
    return query


def catalogObjectFinder(context, **kwargs):
    query = context.query.copy()
    query.update(kwargs)
    query = _normalizeQuery(query)
    catalog = getToolByName(context, 'portal_catalog')
    result = catalog(**query)
    if len(result) == 1:
        return result[0].getObject()
    else:
        return result
