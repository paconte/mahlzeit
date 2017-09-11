# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv
from datetime import datetime
from scrapy.exporters import JsonItemExporter
from scrapy.exporters import CsvItemExporter
from scrapy.exceptions import DropItem
from scrapy.conf import settings
from mahlzeit.db_utils import insert_mongodb


def get_filename():
    pipeline_directory = settings.get('EXPORT_FILES')
    date = datetime.today()
    time_format = "%Y-%m-%d-%H:%M:%S"
    filename = 'mahlzeit'
    return pipeline_directory + filename + '-%s' % date.strftime(time_format)


def clean_item_dish(dish):
    result = dish.replace('\"', '')
    result = dish.replace('"', '')
    result = result.replace('"', '')
    result = result.replace(u'\xa0', u'')
    if result[0] == ' ':
        result = result[1:]
    elif result[-1] == ' ':
        result = result[:-1]
    return result


def clean_item_price(price):
    if price:
        result = price.replace(' ', '')
        result = result.replace('€', '')
    else:
        result = ''
    return result


def clean_item(item):
    item['dish'] = clean_item_dish(item['dish'])
    item.extract_ingredients()
    if 'price' in item:
        item['price'] = clean_item_price(item['price'])
    return item


def validate_menu_item(item):
    if not item['dish'] or len(item['dish'] < 5):
        raise DropItem('Missing %s' % 'dish')
    if not item['location']:
        raise DropItem('Missing %s' % 'location')
    if not item['business']:
        raise DropItem('Missing %s' % 'business')


filename = get_filename()


class JsonExportPipeline(object):
    def __init__(self):
        self.file = open(filename + '.json', 'ab')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        item = clean_item(item)
        self.exporter.export_item(item)
        return item


class CsvExportPipeline(object):
    def __init__(self):
        self.file = open(filename + '.csv', 'ab')
        self.exporter = CsvItemExporter(self.file, encoding='utf-8', join_multivalued=';', quoting=csv.QUOTE_ALL)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        item = clean_item(item)
        self.exporter.export_item(item)
        return item


class MongoDBPipeline(object):

    def process_item(self, item, spider):
        insert_mongodb(item)
        #log.msg("Question added to MongoDB database!", level=log.DEBUG, spider=spider)
        return item
