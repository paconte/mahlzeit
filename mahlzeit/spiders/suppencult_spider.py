import scrapy
from mahlzeit.items import create_dish_for_week
from mahlzeit.items import get_monday_date


class SuppenCultSpider(scrapy.Spider):
    name = "suppencult"
    start_urls = ['http://suppen-cult.de/index.php?page=8']
    business = 'suppencult'

    def parse(self, response):
        names = response.xpath('//div[@class="suppe_name"]/text()').extract()
        prices = response.xpath('//div[@class="suppe_preis"]/text()').extract()
        ingredientsAux = response.xpath('//div[@class="suppe_zutaten"]/text()').extract()
        ingredients = list(ingredientsAux)

        for i in range(len(ingredientsAux)):
            if 'An heißen Sommertagen' in ingredientsAux[i]:
                ingredients.pop(i)
            elif 'Unsere vegetarischen Suppen' in ingredientsAux[i]:
                ingredients.pop(i)

        if len(names) != len(ingredients) or len(names) != len(prices):
            raise KeyError('prices and dishes have different length')

        result = list()
        date = get_monday_date()
        for n, p, i in zip(names, prices, ingredients):
            dish = n + ' ' + i
            result.extend(create_dish_for_week(self.business, dish, date, p))

        return result
