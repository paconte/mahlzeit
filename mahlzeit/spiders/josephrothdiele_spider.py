import scrapy


class JosephRothDieleSpider(scrapy.Spider):
    name = "josephrotdiele"
    start_urls = ['http://joseph-roth-diele.de/wochenkarte-aktuell/']
    business = 'Joseph Rot Diele'
    location = 'Potsdamer Straße'

    def parse(self, response):
        rows = response.xpath('//div[@class="post-entry"]/p').extract()
        print(rows)
