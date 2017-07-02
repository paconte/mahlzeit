# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import JsonItemExporter
from scrapy.exporters import CsvItemExporter
from datetime import datetime


def clean_item_dish(dish):
    result = dish.replace('\"', '')
    result = dish.replace('"', '')
    if result[0] == ' ':
        result = result[1:]
    elif result[-1] == ' ':
        result = result[:-1]
    return result


class JsonExportPipeline(object):
    def __init__(self):
        date = datetime.today()
        filename = 'mahlzeit-%s.json' % date.strftime("%Y-%m-%d")
        self.file = open(filename, 'ab')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        item['dish'] = clean_item_dish(item['dish'])
        self.exporter.export_item(item)
        return item


class CsvExportPipeline(object):
    def __init__(self):
        date = datetime.today()
        filename = 'mahlzeit-%s.csv' % date.strftime("%Y-%m-%d")
        self.file = open(filename, 'ab')
        self.exporter = CsvItemExporter(self.file, encoding='utf-8', join_multivalued=';')
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        item['dish'] = clean_item_dish(item['dish'])
        self.exporter.export_item(item)
        return item
