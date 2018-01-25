import scrapy
import re
from mahlzeit.date_utils import download_and_convert_to_text, get_date
from mahlzeit.date_utils import create_filename_week
from mahlzeit.date_utils import create_dish_for_week
from mahlzeit.date_utils import get_date_of_weekday
from mahlzeit.items import MenuItem


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
        days = list()
        start = False
        dish = ""
        week_days = ['montag\n', 'dienstag\n', 'mittwoch\n', 'donnerstag\n', 'freitag\n']
        for line in text:
            if not start and beginning.match(line):
                start = True
            else:
                if start and not len(line) < 4:
                    if price.match(line):
                        prices.append(clean_price(line))
                        dishes.append(dish)
                        dish = ""
                    elif line.lower() in week_days:
                        day = line[:-1]
                        days.append(day)
                    else:
                        dish += clean_dish(line)
                        if len(dish) > len(days):
                            days.append('all')
        for dish, price, day in zip(dishes, prices, days):
            if day != 'all':
                item = MenuItem(location=location, business=business, dish=dish, date=get_date(date, day),
                                ingredients=list(), price=price)
                items.append(item)
            else:
                items.extend(create_dish_for_week(location, business, dish, date, list(), price))
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
            items.extend(download_and_parse(link, self.name, self.location, self.business, get_date_of_weekday('monday')))
            break
        return items

