# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy


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
