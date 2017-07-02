import scrapy
import re
from subprocess import call
from mahlzeit.items import create_filename_week
from mahlzeit.items import download_and_convert_to_text


class LaPetiteSpider(scrapy.Spider):
    name = "lapetite"
    start_urls = ['http://www.bistro-lapetite.de/downloads/speisekarte.pdf']

    def parse(self, response):
        filename = create_filename_week('la-petite')
        download_and_convert_to_text(response, filename)
        with open(filename, 'r') as f:
            text = f.readlines()
            for line in text:
                print(line)
