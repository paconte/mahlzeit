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
import mahlzeit.db_utils as db
from datetime import datetime
from subprocess import run
from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from mahlzeit.utils import get_file_size
from mahlzeit.utils import send_email


settings = get_project_settings()
process = CrawlerProcess(settings)
log_file = settings.get('LOG_FILE')
spider_list = [
    # spiders for Adlershof
    'albert', 'esswirtschaft', 'jouisnour', 'sonnenschein', 'lapetite', 'cafecampus',
    # spiders for Alex
    'suppencult']


def deploy_in_production():
    run(['cp', settings.get('FRONTEND_FILE'), settings.get('VUEJS_LUNCH_FILE')])
    deploy_script = settings.get('VUEJS_DEPLOY_SCRIPT')
    run(['sh', deploy_script])


class Command(ScrapyCommand):

    requires_project = True
    log_file = settings.get('LOG_FILE')
    email_from = 'paconte@gmail.com'
    email_to = 'paconte@gmail.com'

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'Runs all the production ready spiders of coolinarius'

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option("--deploy", dest="deploy", default=False, action="store_true", help="deploy in to production")
        parser.add_option("--force-deploy", dest="force_deploy", default=False, action="store_true",
                          help="force deploy in to production")
        parser.add_option("--only-deploy", dest="only_deploy", default=False, action="store_true",
                          help="Deploy in to production last status without crawling")

    def run(self, args, opts):
        if opts.only_deploy:
            deploy_in_production()
            return

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

        # create new frontend file
        filename = settings.get('FRONTEND_FILE') + '-' + str(datetime.now()).replace(' ', '-')
        db.print_cursor_to_javascript_file(db.get_current_week_lunches_mongodb(), filename, True)
        run(['cp', filename, settings.get('FRONTEND_FILE')])
        if opts.deploy and db_items_end > db_items_init:
            deploy_in_production()
        elif opts.force_deploy:
            deploy_in_production()



