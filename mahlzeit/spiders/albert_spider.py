import scrapy
import re
from mahlzeit.items import MenuItem
from mahlzeit.date_utils import get_date_of_weekday
from mahlzeit.date_utils import create_dish_for_week
from mahlzeit.date_utils import german_days
from mahlzeit.date_utils import get_current_day_week_number


def extract_dish(row):
    aux = row.xpath('text()').extract()
    result = ''
    if len(aux) > 1:
        for a in aux:
            result += a
    else:
        result = aux[0]
    result = result.replace('\xa0', '')
    return result


def extract_ingredients(ingredients, row):
    result = list(ingredients)
    img_alt = row.xpath('.//img/@alt').extract_first()
    if img_alt and img_alt.lower() == 'vegetarisch':
        result.append('vegetarian')
    return result


def extract_price(row):
    return row.xpath('text()').extract_first()[:-5].replace(',', '.')


def parse_week_number(response):
    exp1 = re.compile(r'Wochentag KW [0-9]+')
    exp2 = re.compile(r'Wochentag KW ')
    text = response.selector.xpath('//table[@id="no-more-tables"]')[0].xpath('.//th').extract_first()
    extract1 = exp1.findall(text)[0]
    if extract1:
        week_number = int(re.sub(exp2, '', extract1))
        return week_number
    # if does not work return the current week
    return get_current_day_week_number()


class AlbertSpider(scrapy.Spider):
    name = "albert"
    start_urls = ['http://www.albert-speisemanufaktur.de/speiseplan']
    business = 'Albert'
    location = 'Adlershof'
    coordinates = [(52.431505, 13.536830)]

    def extract_flammkuchen(self, index, rows, week_number):
        result = list()
        for i in range(index, len(rows)):
            row = rows[i]
            if row.xpath('@data-title').extract_first() == 'Gericht':
                dish = extract_dish(row)
                dish = 'Flammkuchen: ' + dish
                ing_aux = ['Flammkuchen']
                ingredients = extract_ingredients(ing_aux, row)
            elif row.xpath('@data-title').extract_first() == 'Preis':
                price = extract_price(row)
                result.extend(create_dish_for_week(
                    self.location, self.business, dish, get_date_of_weekday('monday', week_number), ingredients, price))
        return result

    def parse(self, response):
        result = list()
        week_number = parse_week_number(response)
        rows1 = response.selector.xpath('//table[@id="no-more-tables"]')[0]
        rows2 = rows1.xpath('.//td')
        item = MenuItem()
        for row in rows2:
            if row.xpath('@data-title').extract_first() == '' and row.xpath('text()').extract_first().lower() \
                    in german_days:
                dish_date = get_date_of_weekday(row.xpath('text()').extract_first(), week_number)
            elif row.xpath('@data-title').extract_first() == '' \
                    and 'flammkuchen' in row.xpath('text()').extract_first().lower():
                result.extend(self.extract_flammkuchen(rows2.index(row), rows2, week_number))
                break
            elif row.xpath('@data-title').extract_first() == 'Gericht':
                item['dish'] = extract_dish(row)
                item['ingredients'] = extract_ingredients(list(), row)
            elif row.xpath('@data-title').extract_first() == 'Preis':
                item['price'] = extract_price(row)
                item['date'] = dish_date
                item['business'] = self.business
                item['location'] = self.location
                result.append(item)
                item = MenuItem()
        return result
