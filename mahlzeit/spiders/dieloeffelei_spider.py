import scrapy
import re
from mahlzeit.items import MenuItem
from mahlzeit.items import get_date_of_weekday
from mahlzeit.items import download_and_convert_to_text
from mahlzeit.items import create_filename_week


days = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag']
price_exp1 = re.compile(r'^[0-9]{1}.*€')


def clean_dish(dish):
    result = dish = dish.replace("\n", "")
    return dish


def clean_price(price):
    result = price[:-3].replace(',','.')
    return result


def parse_weekday_dishes(text, idx1, idx2, weekday, location, business):
    dishes = list()
    dish = ""
    exp1 = re.compile(r'^»')
    for i in range(idx1+1, idx2):
        if exp1.match(text[i]):
            if dish != "":
                dish = clean_dish(dish)
                dishes.append(dish)
            dish = ""
        else:
            dish += text[i]
            if i+1 == idx2:
                dish = clean_dish(dish)
                dishes.append(dish)
    items = list()
    for dish in dishes:
        date = get_date_of_weekday(weekday)
        ingredients = extract_ingredients(dish)
        items.append(MenuItem(location=location ,business=business, dish=dish, price=None, date=date, ingredients=ingredients))
    return items


def parse_prices(text, idx):
    prices = list()
    for i in range(idx, len(text)):
        if price_exp1.match(text[i]):
            prices.append(clean_price(text[i]))
    return prices


def get_indexes(text):
    result = dict()
    for i in range(len(text)):
        line = text[i]
        for day in days:
            if day in line:
                result[day] = i
        if price_exp1.match(text[i]):
            result['Saturday'] = i
            break
    return result


def extract_ingredients(dish):
    result = list()
    exp1 = re.compile(r'Veget')
    exp2 = re.compile(r'Vegan')
    if re.search(exp2, dish):
        result.append('vegan')
        result.append('vegetarian')
    elif re.search(exp1, dish):
        result.append('vegetarian')
    return result


class DieLoeffelei(scrapy.Spider):
    name = "dieloeffelei"
    start_urls = ['https://www.die-loeffelei.de/']
    business = 'Die Loeffelei'
    location = 'Potsdamer Straße'
    coordinates = [(52.502667, 13.365823)]
    
    def parse(self, response):
        link = response.xpath('//div[@class="leftDownload"]/a/@href').extract_first()
        items = list()
        filename = create_filename_week(self.name)
        download_and_convert_to_text(link, filename, True)
        with open(filename, 'r') as f:
            text = f.readlines()
            # find out key indexes to parse the text
            indexes = get_indexes(text)
            # extract items without price
            items.extend(parse_weekday_dishes(text, indexes['Montag'], indexes['Dienstag'], 'Montag', self.location, self.business))
            items.extend(parse_weekday_dishes(text, indexes['Dienstag'], indexes['Mittwoch'], 'Dienstag', self.location, self.business))
            items.extend(parse_weekday_dishes(text, indexes['Mittwoch'], indexes['Donnerstag'], 'Mittwoch', self.location, self.business))
            items.extend(parse_weekday_dishes(text, indexes['Donnerstag'], indexes['Freitag'], 'Donnerstag', self.location, self.business))
            items.extend(parse_weekday_dishes(text, indexes['Freitag'], indexes['Saturday'], 'Freitag', self.location, self.business))
            # extract prices
            prices = parse_prices(text, indexes['Saturday'])
            if len(items) != len(prices):
                print(len(items), len(prices))
                for i in items:
                    print(i['dish'])
                print('##########')
                for i in prices:
                    print(i)
                raise KeyError('prices and dishes have different length')
            # add prices to items
            for item, price in zip(items, prices):
                item['price'] = price
            # return
            return items
