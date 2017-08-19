import scrapy
from mahlzeit.items import MenuItem
from mahlzeit.items import get_date_of_weekday
from mahlzeit.items import create_dish_for_week
from mahlzeit.items import get_monday_date
from mahlzeit.items import days


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
    return row.xpath('text()').extract_first()[:-5].replace(',','.')


class AlbertSpider(scrapy.Spider):
    name = "albert"
    start_urls = ['http://www.albert-speisemanufaktur.de/speiseplan']
    business = 'Albert'
    location = 'Adlershof'

    def extract_flammkuchen(self, index, rows):
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
                    self.location, self.business, dish, get_monday_date(), ingredients, price))
        return result

    def parse(self, response):
        result = list()
        rows1 = response.selector.xpath('//table[@id="no-more-tables"]')[0]
        rows2 = rows1.xpath('.//td')
        item = MenuItem()
        for row in rows2:
            if row.xpath('@data-title').extract_first() == '' and row.xpath('text()').extract_first().lower() in days:
                dish_date = get_date_of_weekday(row.xpath('text()').extract_first())
            elif row.xpath('@data-title').extract_first() == '' \
                    and 'flammkuchen' in row.xpath('text()').extract_first().lower():
                result.extend(self.extract_flammkuchen(rows2.index(row), rows2))
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
