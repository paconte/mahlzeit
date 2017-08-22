"""
Command to run this script: scrapy runspider mahlzeit/all_spider.py

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
from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())

spider_list = [
    # spiders for Adlershof
    'albert', 'esswirtschaft', 'jouisnour', 'sonnenschein', 'lapetite', 'cafecampus',
    # spiders for Alex
    'suppencult']


class Command(ScrapyCommand):

    requires_project = True

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'Runs all of the spiders'

    def run(self, args, opts):
        for spider_name in spider_list:
            process.crawl(spider_name)
        process.start()
