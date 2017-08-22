import scrapy
import re
from mahlzeit.items import download_and_convert_to_text
from mahlzeit.items import create_filename_week
from mahlzeit.items import create_dish_for_week
from mahlzeit.items import get_monday_date


def clean_price(line):
    return line[:-3].replace(',', '.')


def clean_dish(line):
    return line[:-1]


def download_and_parse(link, name, location, business, date):
    items = list()
    filename = create_filename_week(name)
    download_and_convert_to_text(link, filename, True)
    with open(filename, 'r') as f:
        text = f.readlines()
        beginning = re.compile(r'^Wochenkarte')
        price = re.compile(r'^[0-9].*€')
        prices = list()
        dishes = list()
        start = False
        dish = ""
        for line in text:
            if not start and beginning.match(line):
                start = True
            else:
                if start and not len(line) < 4:
                    if price.match(line):
                        prices.append(clean_price(line))
                        dishes.append(dish)
                        dish = ""
                    else:
                        dish += clean_dish(line)
        for d, p in zip(dishes, prices):
            items.extend(create_dish_for_week(location, business, d, date, list(), p))
    return items


class CafeCampusSpider(scrapy.Spider):
    name = "cafecampus"
    start_urls = ['https://www.cafe-campus-adlershof.de/speisen-getränke/wochenkarte/']
    business = 'Cafe Campus'
    location = 'Adlershof'
    coordinates = [(52.435679, 13.529603)]

    def parse(self, response):
        items = list()
        rows = response.xpath('//div[@class="rightDownload"]')
        for r in rows:
            link = r.xpath('./a/@href').extract_first()
            items.extend(download_and_parse(link, self.name, self.location, self.business, get_monday_date()))
            break
        return items

