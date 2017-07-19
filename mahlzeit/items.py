# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from datetime import datetime
from datetime import timedelta
from subprocess import call


vegetarian_words = ['vegetarisch', 'vegan']
vegan_words = ['vegan']
fish_words = ['fisch', 'lachs', 'oktopus']
soup_words = ['suppe', 'soljanka']


class MenuItem(scrapy.Item):
    location = scrapy.Field()
    business = scrapy.Field()
    date = scrapy.Field()
    dish = scrapy.Field()
    price = scrapy.Field()
    ingredients = scrapy.Field()

    def capitalize_ingredients(self):
        result = list()
        for ingr in self['ingredients']:
            result.append(ingr.capitalize())
        self['ingredients'] = result

    def extract_ingredients(self):
        result = set()
        dish_lower = self['dish'].lower()
        for word in vegetarian_words:
            if word in dish_lower:
                result.add('vegetarian')
        for word in vegan_words:
            if word in dish_lower:
                result.add('vegan')
        for word in fish_words:
            if word in dish_lower:
                result.add('fish')
        for word in soup_words:
            if word in dish_lower:
                result.add('soup')
        for ing in self['ingredients']:
            result.add(ing.lower())
        self['ingredients'] = list(result)


days = ['montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag']


def create_filename_week(base, weeks=0):
    kw = datetime.today().isocalendar()[1]
    return '%s-kw%s.txt' % (str(base), str(kw))


def download_and_convert_to_text(response, dst_file):
    filename = 'download.pdf'
    with open(filename, 'wb') as f:
        f.write(response.body)
    call(["rm", dst_file])
    call(["pdftotext", filename, dst_file])
    call(["rm", filename])


def create_dish_for_week(location, business, dish, date, ingredients=list(), price=None):
    result = list()
    for day in days:
        item = MenuItem(location=location, business=business, dish=dish, date=get_date(date, day), ingredients=ingredients, price=price)
        result.append(item)
    return result


def get_date(date, weekday):
    day = weekday.lower()
    if (day not in days):
        raise TypeValueException('Wrong week day.')
    days_to_add = days.index(day)
    return (date + timedelta(days=days_to_add)).strftime('%d.%m.%Y')


def get_monday_date(weeks=0):
    date = datetime.today() + timedelta(weeks=weeks)
    weekday = date.weekday()
    monday_date = date - timedelta(days=weekday)
    return monday_date


def get_date_of_weekday(weekday, weeks=0):
    """Returns the date of a given weekday (like monday or wednesday) of the current week or a future/past week

    Parameters
    ----------
    weekday : str
    weeks : int, optional

    Returns
    -------
    date
    The date of the given weekday(parameter) on the current week with a delta of weeks(parameter)
    """
    monday = get_monday_date(weeks)
    return get_date(monday, weekday)
