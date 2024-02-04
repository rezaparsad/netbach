import re

import jdatetime

from .shortlink_model import ShortLink


def create_short_link(url):
    ShortLink.objects.create(link=url)


def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return ((re.sub(clean, '', text)
            .replace("&nbsp;", "")
            .replace("&zwnj;", ""))
            .replace("&quot;", ""))


def get_date_persian(date):
    date = jdatetime.datetime.fromgregorian(datetime=date)
    return str(date.day) + " " + date.j_months_fa[date.month - 1] + " " + str(date.year)


def sort_price(datamatch, max=False):
    new_data_match = []
    for data in datamatch:
        data.price = int(data.price)
        new_data_match.append(data)

    new_list = sorted(new_data_match, key=lambda k: k.price, reverse=max)
    return new_list


class DatacenterPackage:
    def __init__(self, name):
        self.name = name
        self.servers = []
        self.locations = []
