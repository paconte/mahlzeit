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
import os
import smtplib
import mahlzeit.db_utils as db
from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from email.mime.text import MIMEText


settings = get_project_settings()
process = CrawlerProcess(settings)
log_file = settings.get('LOG_FILE')
spider_list = [
    # spiders for Adlershof
    'albert', 'esswirtschaft', 'jouisnour', 'sonnenschein', 'lapetite', 'cafecampus',
    # spiders for Alex
    'suppencult']


class Command(ScrapyCommand):

    requires_project = True
    log_file = settings.get('LOG_FILE')
    email_from = 'paconte@gmail.com'
    email_to = 'paconte@gmail.com'

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'Runs all the production ready spiders of coolinarius'

    def run(self, args, opts):
        # create database backup
        db.create_mongodb_backup()

        # save size of log file and number of items at the db
        log_size_init = get_file_size(log_file)
        db_items_init = db.count_lunches(db.get_current_week_lunches_mongodb())
        # crawl and insert in the db
        for spider_name in spider_list:
            process.crawl(spider_name)
        process.start()

        # save new sizes of log file and items at the db
        log_size_end = get_file_size(log_file)
        db_items_end = db.count_lunches(db.get_current_week_lunches_mongodb())

        # if the log file has new entries send an email to notify
        if log_size_init < log_size_end:
            send_email(self.email_from, self.email_to)

        # create new file
        db.print_cursor_to_file(db.get_current_week_lunches_mongodb(), settings.get('FRONTEND_FILE'), True)

        if db_items_end > db_items_init:
            # deploy new version
            pass


def get_file_size(filename):
    return os.stat(filename).st_size


def send_email(email_from, email_to):
    with open(log_file, 'rt') as fp:
        msg = MIMEText(fp.read())
    msg['Subject'] = 'Exceptions while crawling coolinarius.'
    msg['From'] = email_from
    msg['To'] = email_to
    server = smtplib.SMTP('localhost')
    server.sendmail(email_from, [email_to], msg.as_string())
    server.quit()
