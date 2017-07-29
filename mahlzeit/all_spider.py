"""
new possible spiders:
https://www.lokali.de/berlin/mittagstisch
https://www.tip-berlin.de/lunchtime-die-besten-adressen-berlin/
kudamm:
http://www.kurfuerstendamm.de/berlin/essen_trinken/mittagstisch/
potsdamerplatz:
https://www.dein-alex.de/wochenkarte-berlin-sonycenter
alex:
https://www.dein-alex.de/wochenkarte-alex-berlin-am-alexanderplatz
http://www.pureorigins.de
http://www.kult-curry.de
mitte:
http://www.samadhi-vegetarian.de
http://hummus-and-friends.com/menu/
http//avanberlin.com/
hbf:
http://www.paris-moskau.de/sites/restaurant_paris_moskau_kontakt.htm
weißensee:
www.cook-berlin.de/mittagstisch/
"""
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

# adlershof
process.crawl(AlbertSpider)
process.crawl(EWSpider)
process.crawl(JouisNourSpider)
process.crawl(SonnenscheinSpider)
process.crawl(LaPetiteSpider)
# alex
process.crawl(SuppenCultSpider)

process.start()
