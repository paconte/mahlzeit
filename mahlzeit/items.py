# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import urllib.request
from datetime import datetime
from datetime import timedelta
from subprocess import call
from scrapy.utils.project import get_project_settings


settings = get_project_settings()

vegetarian_words = ['vegetarisch', 'vegan']
vegan_words = ['vegan']
fish_words = ['fisch', 'lachs', 'oktopus', 'kabeljau', 'rotbarsch', 'forelle', 'zander']
soup_words = ['suppe', 'soljanka', 'borschtsch']
dessert_words = ['milschreis', 'grießbrei', 'kirschen', 'tiramisu']


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
        # iterate words
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
        for word in dessert_words:
            if word in dish_lower:
                result.add('dessert')
        # add old ingredients
        for ing in self['ingredients']:
            result.add(ing.lower())
        # set new ingredients
        self['ingredients'] = list(result)
        self.capitalize_ingredients()


german_days = ['montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag']
english_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']


def create_filename_week(base, weeks=0):
    path = settings.get('EXPORT_FILES')
    kw = datetime.today().isocalendar()[1]
    return path + '%s-kw%s.txt' % (str(base), str(kw))


def download_and_convert_to_text(file, dst_file, download=False):
    path = settings.get('EXPORT_FILES')
    filename = path + 'download.pdf'
    if download:
        file = urllib.request.urlopen(file).read()
    with open(filename, 'wb') as f:
        f.write(file)
    call(["rm", dst_file])
    call(["pdftotext", filename, dst_file])
    call(["rm", filename])


def create_dish_for_week(location, business, dish, date=None, ingredients=list(), price=None):
    result = list()
    for day in german_days:
        item = MenuItem(location=location, business=business, dish=dish, date=get_date(date, day),
                        ingredients=ingredients, price=price)
        result.append(item)
    return result


def get_date(date, weekday):
    day = weekday.lower()
    if day not in german_days:
        raise ValueError('Wrong week day.')
    days_to_add = german_days.index(day)
    result = date + timedelta(days=days_to_add)
    return result


def days_to_add_to_monday(weekday):
    day = weekday.lower()
    if day in german_days:
        days_to_add = german_days.index(day)
    elif day in english_days:
        days_to_add = english_days.index(day)
    else:
        raise ValueError('Wrong week day.')
    return days_to_add


def get_monday_date_from_week_number(week_number):
    year = datetime.today().year
    date_str = str(year) + '-' + str(week_number) + '-1'
    result = datetime.strptime(date_str, "%Y-%W-%w")
    return result


def get_monday_date(weeks=0):
    date = get_today_midnight() + timedelta(weeks=weeks)
    weekday = date.weekday()
    monday_date = date - timedelta(days=weekday)
    return monday_date


def get_date_of_weekday(weekday, week_number=-1, week_delta=0):
    """
    Returns the date of a given weekday (like monday or wednesday) of the given calendar week if week>-1 otherwise the
    current week is used. It is possible to add a week delta, e.g. week_delta = -1 means one week before and
    week_delta = 2 two weeks in the future.

    Parameters
    ----------
    weekday : str
    week_number: int, optional
    week_delta : int, optional

    Returns
    -------
    date
    The date of the given weekday(parameter) on the current week or week number with a delta of weeks(parameter)
    """
    days_to_add = days_to_add_to_monday(weekday)
    if week_number > -1:
        monday = get_monday_date_from_week_number(week_number)
        # result = monday + timedelta(days=days_to_add) + timedelta(weeks=week_delta)
    else:
        monday = get_monday_date(week_delta)
        # result = get_date(monday, weekday)
    result = monday + timedelta(days=days_to_add) + timedelta(weeks=week_delta)
    return result


def get_today_midnight():
    return datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)


def get_current_week_number():
    return datetime.today().isocalendar()[1]
