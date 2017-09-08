import os
from scrapy.spiders import CSVFeedSpider
from mahlzeit.items import MenuItem
from dateutil.parser import parse
from scrapy.utils.project import get_project_settings


class JouisNourSpider(CSVFeedSpider):
    name = "jouisnour"
    start_urls = ['file://' + os.getcwd() + '/' + get_project_settings()['IMPORT_FILES'] + 'jouisnour.csv']
    # start_urls = ['file:///home/frevilla/devel/scrapy/mahlzeit/data/import/jouisnour.csv']
    headers = ['date', 'location', 'business', 'price', 'type', 'name']
    delimiter = ';'
    coordinates = [(52.432440, 13.534732)]
    custom_settings = {'ROBOTSTXT_OBEY': 'False'}

    def parse_row(self, response, row):
        # skip headers
        if row['date'] == 'date' and row['location'] == 'location':
            return
        # extract ingredients
        types = row['type']
        types = types.split(',')
        ingredients = list()
        for t in types:
            t = t.replace(' ', '')
            if len(t) > 1:
                ingredients.append(t.replace(' ', ''))
        # create item
        item = MenuItem()
        item['date'] = parse(row['date'])
        item['location'] = row['location']
        item['business'] = row['business']
        item['price'] = row['price']
        item['dish'] = row['name']
        item['ingredients'] = ingredients
        return item
