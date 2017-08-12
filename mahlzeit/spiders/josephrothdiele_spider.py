import scrapy
from mahlzeit.items import MenuItem
from mahlzeit.items import get_date_of_weekday
from mahlzeit.items import create_dish_for_week
from mahlzeit.items import get_monday_date
from mahlzeit.items import days


class JosephRothDieleSpider(scrapy.Spider):
    name = "josephrotdiele"
    start_urls = ['http://joseph-roth-diele.de/wochenkarte-aktuell/']
    business = 'Joseph Rot Diele'
    location = 'Potsdamer Straße'

    def parse(self, response):
        rows = response.xpath('//div[@class="post-entry"]/p').extract()
        print(rows)
