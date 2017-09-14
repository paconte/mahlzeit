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
from subprocess import call
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


def create_frontend_files():
    lunches_file = settings.get('FRONTEND_LUNCHES') + '-' + str(datetime.now()).replace(' ', '-')
    cursor = db.get_current_week_lunches_mongodb()
    print(str(cursor.count()) + ' item(s) exported to frontend.')
    db.print_cursor_to_javascript_file(cursor, lunches_file, True)
    call(['cp', lunches_file, settings.get('FRONTEND_LUNCHES')])
    db.print_coordinates(settings.get('FRONTEND_COORDINATES'))


def deploy_in_production():
    # create new frontend files
    create_frontend_files()
    # copy files to VUEJS
    call(['cp', settings.get('FRONTEND_LUNCHES'), settings.get('VUEJS_LUNCH_FILE')])
    call(['cp', settings.get('FRONTEND_COORDINATES'), settings.get('VUEJS_COORDINATES_FILE')])
    # call deploy script
    deploy_script = settings.get('VUEJS_DEPLOY_SCRIPT')
    call(['sh', deploy_script])


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
        parser.add_option("--run", dest="run", default=False, action="store_true", help="run all coolinarius crawlers")
        parser.add_option("--backup", dest="backup", default=False, action="store_true",
                          help="Create database backup before inserting any item")
        parser.add_option("--import", type=str, dest="import_collection",
                          help="Import a collection of lunches from a file to the database")
        parser.add_option("--frontend", dest="frontend", default=False, action="store_true",
                          help="Create file for frontend VUEJS")
        parser.add_option("--email", dest="email", default=False, action="store_true",
                          help="Send e-mail if log file is changed.")
        parser.add_option("--deploy", dest="deploy", default=False, action="store_true", help="deploy in to production")
        parser.add_option("--force-deploy", dest="force_deploy", default=False, action="store_true",
                          help="force deploy in to production")
        parser.add_option("--only-deploy", dest="only_deploy", default=False, action="store_true",
                          help="Deploy in to production last status without crawling")
        parser.add_option("--db-new-collection", dest="new_collection", default=False, action="store_true",
                          help="Drop lunch collections and creates a new one")

    def run_crawlers(self, opts):
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
        if opts.email and log_size_init < log_size_end:
            send_email(self.email_from, self.email_to)

        # deploy into production
        if opts.deploy and db_items_end > db_items_init:
            deploy_in_production()
        elif opts.force_deploy:
            deploy_in_production()

    def run(self, args, opts):
        if opts.only_deploy:
            deploy_in_production()
            return
        if opts.new_collection:
            db.create_collection()
            return
        if opts.import_collection:
            print("Importing file %s into collection lunch." % opts.import_collection)
            db.import_lunches(opts.import_collection)
            return
        if opts.frontend:
            create_frontend_files()
            return
        if opts.backup:
            db.export_lunches()
        if opts.run:
            self.run_crawlers(opts)
            return


