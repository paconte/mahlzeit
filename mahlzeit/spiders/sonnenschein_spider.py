import scrapy
import re
from mahlzeit.items import MenuItem
from mahlzeit.items import get_date_of_weekday
from mahlzeit.items import download_and_convert_to_text
from mahlzeit.items import create_filename_week


def _clean_dish_string(string):
    string = string[:-1]
    exp = re.compile(r'^[0-9]{1}')
    string = re.sub(exp, '', string)
    exp = re.compile(r'^(\.)?')
    string = re.sub(exp, '', string)
    exp = re.compile(r'^( – )?')
    string = re.sub(exp, '', string)
    exp = re.compile(r'^(– )?')
    string = re.sub(exp, '', string)
    exp = re.compile(r'^( –)?')
    string = re.sub(exp, '', string)
    return string


def extract_price_at_end(text):
    price = re.search(r' [0-9]{1}.*€', text)
    dish = text
    if price:
        price = price.group(0)[1:-1].replace(',', '.')
        dish = re.sub(r' [0-9]{1}.*€', '', text)
    return dish, price


def extract_ingredients(dishes):
    result = list()
    for text in dishes:
        subresult = list()
        exp1 = re.compile(r'\(vegetarisch\)|vegetarisch')
        found = re.search(exp1, text)
        if found:
            subresult.append('vegetarian')
        result.append(subresult)
    return result


def parse_weekday(location, business, text, idx1, idx2, weekday):
    date = get_date_of_weekday(weekday)
    exp1 = re.compile(r'^Tagessuppe: ')
    exp2 = re.compile(r'^[0-9]{1}(\.)?[ – |– |-]')
    exp3 = re.compile(r'^[a-zA-Z]+')
    price_exp1 = re.compile(r'^[0-9]{1}.*€')

    prices = list()
    dishes = list()
    is_last_dish = False
    for i in range(idx1, idx2):
        if exp1.match(text[i]):
            is_last_dish = True
            dish = re.sub(exp1, '', text[i])[:-1]
            dishes.append(dish)
        elif exp2.match(text[i]):
            is_last_dish = True
            text[i], price = extract_price_at_end(text[i])
            dish = _clean_dish_string(text[i])
            dishes.append(dish)
            if price:
                prices.append(price)
        elif exp3.match(text[i]) and is_last_dish:
            is_last_dish = True
            dishes[-1] = dishes[-1] + ' ' + text[i][:-1]
        elif price_exp1.match(text[i]):
            is_last_dish = False
            price = text[i][:-2].replace(',', '.')
            prices.append(price)

    if len(prices) != len(dishes):
        raise KeyError('prices and dishes have different length')

    ingredients = extract_ingredients(dishes)
    result = list()
    for d, p, i in zip(dishes, prices, ingredients):
        item = MenuItem(location=location, business=business, dish=d, price=p, date=date, ingredients=i)
        result.append(item)
    return result


class SonnenscheinSpider(scrapy.Spider):
    name = "sonnenschein"
    start_urls = ['http://www.adlershof.de/fileadmin/user_upload/downloads/essen/sonnenschein.pdf']
    business = 'Sonnenschein'
    location = 'Adlershof'

    def parse(self, response):
        items = list()
        filename = create_filename_week('sonnenschein')
        download_and_convert_to_text(response.body, filename)
        days = ['Montag\n', 'Dienstag\n', 'Mittwoch\n', 'Donnerstag\n', 'Freitag\n']
        with open(filename, 'r') as f:
            text = f.readlines()
            for i in range(len(days)):
                try:
                    idx2 = text.index(days[i+1])
                except IndexError:
                    idx2 = len(text)
                idx1 = text.index(days[i])
                items += parse_weekday(self.location, self.business, text, idx1, idx2, days[i][:-1])
        return items
