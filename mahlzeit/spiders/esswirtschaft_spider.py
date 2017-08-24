import scrapy
from mahlzeit.items import MenuItem
from mahlzeit.date_utils import get_date_of_weekday
from mahlzeit.date_utils import create_dish_for_week


def extract_ingredients(dish):
    ingredients = list()
    dish_aux = dish
    if '**' in dish:
        ingredients.append('vegan')
        ingredients.append('vegetarian')
        dish_aux = dish.replace('*', '')
    elif '*' in dish:
        ingredients.append('vegetarian')
        dish_aux = dish.replace('*', '')
    return dish_aux, ingredients


class EWSpider(scrapy.Spider):
    name = "esswirtschaft"
    start_urls = ['http://www.esswirtschaft.de/wochenkarte/wochenkarte.html']
    business = 'Esswirtschaft'
    location = 'Adlershof'
    coordinates = [(52.431399, 13.532762)]

    def create_item(self, dish, date):
        dish_aux, ingredients = extract_ingredients(dish)
        return MenuItem(dish=dish_aux, date=date, ingredients=ingredients, location=self.location, business=self.business)

    def parse(self, response):
        result = list()
        monday = get_date_of_weekday('monday')
        # wochengericht
        wochengericht = response.selector.xpath('//h2[1]//following-sibling::p[1]//text()').extract_first()
        wochengericht, ingredients = extract_ingredients(wochengericht)
        result.extend(create_dish_for_week(self.location, self.business, wochengericht, monday, ingredients))
        # wochensalat
        wochensalat = response.selector.xpath('//h2[2]//following-sibling::p[1]//text()').extract_first()
        wochensalat, ingredients = extract_ingredients(wochensalat)
        result.extend(create_dish_for_week(self.location, self.business, wochensalat, monday, ingredients))
        # salat im Glas
        salat_im_glas = response.selector.xpath('//h2[3]//following-sibling::p[1]//text()').extract_first()
        salat_im_glas, ingredients = extract_ingredients(salat_im_glas)
        result.extend(create_dish_for_week(self.location, self.business, salat_im_glas, monday, ingredients))
        # wochensuppen
        wochensuppe1 = response.selector.xpath('//h3//following-sibling::p[1]')[1].extract()[3:-4]
        wochensuppe1, ingredients = extract_ingredients(wochensuppe1)
        wochensuppe2 = response.selector.xpath('//h3//following-sibling::p[2]//text()').extract_first()
        wochensuppe2, ingredients = extract_ingredients(wochensuppe2)
        wochensuppe3 = response.selector.xpath('//h3//following-sibling::p[3]//text()').extract_first()
        wochensuppe3, ingredients = extract_ingredients(wochensuppe3)
        result.extend(create_dish_for_week(self.location, self.business, wochensuppe1, monday, ingredients))
        result.extend(create_dish_for_week(self.location, self.business, wochensuppe2, monday, ingredients))
        result.extend(create_dish_for_week(self.location, self.business, wochensuppe3, monday, ingredients))

        # montag
        monday = response.selector.xpath('//h2[4]//following-sibling::p[1]//text()').extract_first()
        item = self.create_item(monday, get_date_of_weekday('montag'))
        result.append(item)
        monday = response.selector.xpath('//h2[4]//following-sibling::p[2]//text()').extract_first()
        item = self.create_item(monday, get_date_of_weekday('montag'))
        result.append(item)
        # dienstag
        tuesday = response.selector.xpath('//h2[5]//following-sibling::p[1]//text()').extract_first()
        item = self.create_item(tuesday, get_date_of_weekday('dienstag'))
        result.append(item)
        tuesday = response.selector.xpath('//h2[5]//following-sibling::p[2]//text()').extract_first()
        item = self.create_item(tuesday, get_date_of_weekday('dienstag'))
        result.append(item)
        # mittwoch
        wednesday = response.selector.xpath('//h2[6]//following-sibling::p[1]//text()').extract_first()
        item = self.create_item(wednesday, get_date_of_weekday('mittwoch'))
        result.append(item)
        wednesday = response.selector.xpath('//h2[6]//following-sibling::p[2]//text()').extract_first()
        item = self.create_item(wednesday, get_date_of_weekday('mittwoch'))
        result.append(item)
        # donnerstag
        thursday = response.selector.xpath('//h2[7]//following-sibling::p[1]//text()').extract_first()
        item = self.create_item(thursday, get_date_of_weekday('donnerstag'))
        result.append(item)
        thursday = response.selector.xpath('//h2[7]//following-sibling::p[2]//text()').extract_first()
        item = self.create_item(thursday, get_date_of_weekday('donnerstag'))
        result.append(item)
        # freitag
        friday = response.selector.xpath('//h2[8]//following-sibling::p[1]//text()').extract_first()
        item = self.create_item(friday, get_date_of_weekday('freitag'))
        result.append(item)
        friday = response.selector.xpath('//h2[8]//following-sibling::p[2]//text()').extract_first()
        item = self.create_item(friday, get_date_of_weekday('freitag'))
        result.append(item)

        return result
