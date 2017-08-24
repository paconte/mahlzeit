import scrapy
import re
from mahlzeit.date_utils import create_filename_week
from mahlzeit.date_utils import download_and_convert_to_text
from mahlzeit.date_utils import german_days
from mahlzeit.date_utils import create_dish_for_week
from mahlzeit.date_utils import get_date_of_weekday


def prepare_text(filename):
    # read file data
    with open(filename, 'r') as file:
        filedata = file.read()
        # replace file data
        filedata = filedata.replace('– ', '')
        filedata = filedata.replace(' –', '')
        filedata = filedata.replace('- ', '')
        filedata = filedata.replace('–', '')
        filedata = filedata.replace('-', '')
        filedata = filedata.replace('EURO ', 'euros\n')
        filedata = filedata.replace('Euro ', 'euros\n')
        filedata = filedata.replace('EURO', 'euros\n')
        filedata = filedata.replace('Euro', 'euros\n')
    # write file data
    with open(filename, 'w') as file:
        file.write(filedata)


def extract_idxs(filename):
    idxs = list()
    with open(filename, 'r') as f:
        text = f.readlines()
        for i in range(len(text)):
            if text[i].find('Lunch ab') > -1 or text[i].find('euros') > -1:
                idxs.append(i)
    return idxs


def extract_info(location, business, idx1, idx2, text):
    exp1 = re.compile(r'\((.*)\)')
    dish = ''
    for i in range(idx1, idx2):
        ignore = False
        for day in german_days:
            lower_line = text[i].lower()
            if lower_line.find(day) > -1:
                ignore = True
        if i != idx1 and not ignore:
            dish += text[i].replace('\n', ' ')

    dish = re.sub(exp1, ' ', dish)
    if dish[0] == ' ':
        dish = dish[1:]
    price = text[i+1].replace('euros', '')
    price = price.replace(' ', '')
    price = price.replace('\n', '')
    date = get_date_of_weekday('monday')
    ingredients = list()
    return create_dish_for_week(location, business, dish, date, ingredients, price)


class LaPetiteSpider(scrapy.Spider):
    name = "lapetite"
    business = 'La Petite'
    location = 'Adlershof'
    start_urls = ['http://www.bistro-lapetite.de/downloads/speisekarte.pdf']
    coordinates = [(52.430156, 13.541748)]

    def parse(self, response):
        items = list()
        # convert picture in text
        filename = create_filename_week('la-petite')
        download_and_convert_to_text(response.body, filename)
        # clean original picture text
        prepare_text(filename)
        # extract key idexes of text
        idxs = extract_idxs(filename)
        # extract info
        with open(filename, 'r') as f:
            text = f.readlines()
        for i in range(len(idxs)):
            idx1 = idxs[i]
            try:
                idx2 = idxs[i+1]
            except IndexError:
                break
            items.extend(extract_info(self.location, self.business, idx1, idx2, text))
        return items
