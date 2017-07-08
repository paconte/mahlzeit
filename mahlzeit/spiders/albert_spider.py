import scrapy
from mahlzeit.items import MenuItem
from mahlzeit.items import get_date_of_weekday
from mahlzeit.items import days

class AlbertSpider(scrapy.Spider):
    name = "albert"
    start_urls = ['http://www.albert-speisemanufaktur.de/speiseplan']
    business = 'albert'

    def parse(self, response):
        result = list()
        rows = response.selector.xpath('//table[@id="no-more-tables"]//td')
        item = MenuItem()
        for row in rows:
            if row.xpath('@data-title').extract_first() == '' and row.xpath('text()').extract_first().lower() in days:
                dish_date = get_date_of_weekday(row.xpath('text()').extract_first())
            elif (row.xpath('@data-title').extract_first() == 'Gericht'):
                item['dish'] = row.xpath('text()').extract_first()
                item['ingredients'] = list()
                img_alt = row.xpath('.//img/@alt').extract_first()
                if img_alt and img_alt.lower() == 'vegetarisch':
                    item['ingredients'].append('vegetarian')
            elif (row.xpath('@data-title').extract_first() == 'Preis'):
                item['price'] = row.xpath('text()').extract_first()[:-5].replace(',','.')
                item['date'] = dish_date
                item['business'] = self.business
                result.append(item)
                item = MenuItem()
        return result
