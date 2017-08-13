# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv
from scrapy.exporters import JsonItemExporter
from scrapy.exporters import CsvItemExporter
from scrapy.utils.project import get_project_settings
from datetime import datetime


def get_filename(type):
    settings = get_project_settings()
    pipeline_directory = settings.get('EXPORT_FILES')
    date = datetime.today()
    if type == 'csv':
        result = pipeline_directory + 'mahlzeit-%s.csv' % date.strftime("%Y-%m-%d")
    elif type == 'json':
        result = pipeline_directory + 'mahlzeit-%s.json' % date.strftime("%Y-%m-%d")
    else:
        raise AttributeError('Wrong argument %s' % type)
    return result


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


class JsonExportPipeline(object):
    def __init__(self):
        filename = get_filename('json')
        self.file = open(filename, 'ab')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        item['dish'] = clean_item_dish(item['dish'])
        item.extract_ingredients()
        if 'price' in item:
            item['price'] = clean_item_price(item['price'])
        self.exporter.export_item(item)
        return item


class CsvExportPipeline(object):
    def __init__(self):
        filename = get_filename('csv')
        self.file = open(filename, 'ab')
        self.exporter = CsvItemExporter(self.file, encoding='utf-8', join_multivalued=';', quoting=csv.QUOTE_ALL)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        item['dish'] = clean_item_dish(item['dish'])
        item.extract_ingredients()
        if 'price' in item:
            item['price'] = clean_item_price(item['price'])
        self.exporter.export_item(item)
        return item
