import scrapy
from datetime import datetime
from mahlzeit.items import MenuItem
from mahlzeit.items import get_date, get_date_of_weekday
from mahlzeit.items import create_dish_for_week
from mahlzeit.items import get_monday_date
from mahlzeit.items import days

class EWSpider(scrapy.Spider):
    name = "esswirtschaft"
    start_urls = ['http://www.esswirtschaft.de/wochenkarte/wochenkarte.html']
    business = 'esswirtschaft'

    def parse(self, response):
        result = list()
        # wochengericht
        wochengericht = response.selector.xpath('//h2[1]//following-sibling::p[1]//text()').extract_first()
        result.extend(create_dish_for_week(self.business, wochengericht, get_monday_date()))
        # wochensalat
        wochensalat = response.selector.xpath('//h2[2]//following-sibling::p[1]//text()').extract_first()
        result.extend(create_dish_for_week(self.business, wochensalat, get_monday_date()))
        # salat im Glas
        salat_im_glas = response.selector.xpath('//h2[3]//following-sibling::p[1]//text()').extract_first()
        result.extend(create_dish_for_week(self.business, salat_im_glas, get_monday_date()))
        # wochensuppen
        wochensuppe1 = response.selector.xpath('//h3//following-sibling::p[1]')[1].extract()[3:-4]
        wochensuppe2 = response.selector.xpath('//h3//following-sibling::p[2]//text()').extract_first()
        wochensuppe3 = response.selector.xpath('//h3//following-sibling::p[3]//text()').extract_first()
        result.extend(create_dish_for_week(self.business, wochensuppe1, get_monday_date()))
        result.extend(create_dish_for_week(self.business, wochensuppe2, get_monday_date()))
        result.extend(create_dish_for_week(self.business, wochensuppe3, get_monday_date()))

        # montag
        monday = response.selector.xpath('//h2[4]//following-sibling::p[1]//text()').extract_first()
        item = MenuItem(dish=monday, date=get_date_of_weekday('montag'), business=self.business)
        result.append(item)
        # dienstag
        tuesday = response.selector.xpath('//h2[5]//following-sibling::p[1]//text()').extract_first()
        item = MenuItem(dish=tuesday, date=get_date_of_weekday('dienstag'), business=self.business)
        result.append(item)
        # mittwoch
        wednesday = response.selector.xpath('//h2[6]//following-sibling::p[1]//text()').extract_first()
        item = MenuItem(dish=wednesday, date=get_date_of_weekday('mittwoch'), business=self.business)
        result.append(item)
        # donnerstag
        thursday = response.selector.xpath('//h2[7]//following-sibling::p[1]//text()').extract_first()
        item = MenuItem(dish=thursday, date=get_date_of_weekday('donnerstag'), business=self.business)
        result.append(item)
        # freitag
        friday = response.selector.xpath('//h2[8]//following-sibling::p[1]//text()').extract_first()
        item = MenuItem(dish=friday, date=get_date_of_weekday('freitag'), business=self.business)
        result.append(item)

        return result
