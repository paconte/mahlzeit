import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from mahlzeit.spiders.albert_spider import AlbertSpider
from mahlzeit.spiders.esswirtschaft_spider import EWSpider
from mahlzeit.spiders.sonnenschein_spider import SonnenscheinSpider
from mahlzeit.spiders.jouisnour_spider import JouisNourSpider
from mahlzeit.spiders.lapetite_spider import LaPetiteSpider
from mahlzeit.spiders.suppencult_spider import SuppenCultSpider


process = CrawlerProcess(get_project_settings())

process.crawl(AlbertSpider)
process.crawl(EWSpider)
process.crawl(JouisNourSpider)
process.crawl(SuppenCultSpider)
process.crawl(SonnenscheinSpider)
process.crawl(LaPetiteSpider)

process.start()
