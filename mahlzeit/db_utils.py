import logging
import pymongo
from datetime import datetime
from datetime import timedelta
from subprocess import call
from bson.json_util import dumps
from scrapy.conf import settings
from mahlzeit.date_utils import get_today_midnight
from mahlzeit.date_utils import get_date_of_weekday
from mahlzeit.date_utils import get_current_day_week_number
from mahlzeit.date_utils import is_weekend
from mahlzeit.date_utils import get_monday_date

connection = pymongo.MongoClient(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
database = connection[settings['MONGODB_DB']]
collection = database[settings['MONGODB_COLLECTION']]


def print_cursor_to_javascript_file(cursor, dst, variable=False):
    obj = dumps(cursor)
    with open(dst, "w") as fp:
        if variable:
            fp.write('const productsAux = \'')
            fp.write(obj)
            fp.write('\';\nconst products = JSON.parse(productsAux);\n')
            fp.write('export default products;\n')
        else:
            fp.write(obj)


def count_lunches(lunches, list_business=None, weekday_start=None):
    if isinstance(lunches, dict):
        result = dict()
        for key, cursor in lunches.items():
            result[key] = cursor.count()
    else:
        result = lunches.count()
    return result


def get_next_week_lunches_mongodb():
    start_date = get_monday_date(1)
    end_date = start_date + timedelta(days=6, hours=23)
    result = collection.find({"date": {"$gte": start_date, "$lte": end_date}})
    return result


def get_current_week_lunches_mongodb(list_business=None, weekday_start=None):
    # calculate start and finish date
    if not weekday_start:
        start_date = get_today_midnight()
    else:
        start_date = get_date_of_weekday('monday')
    end_date = get_date_of_weekday('friday')
    # perform query
    if list_business:
        result = dict()
        for business in list_business:
            result[business] = collection.find({"business": business,
                                                "date": {"$gte": start_date, "$lte": end_date}})
    else:
        result = collection.find({"date": {"$gte": start_date, "$lte": end_date}})
        # result = collection.find({"date": {"$gte": start_date}})
    return result


def insert_mongodb(item):
    list_business = list()
    list_business.append(item['business'])
    records = get_current_week_lunches_mongodb(list_business)
    current_week = get_current_day_week_number()
    insert = False

    # item belongs to next week but date is wrong
    if is_weekend() and item['date'].isocalendar()[1] == current_week:
        not_found = False
        cursor = records[item['business']]
        for record in cursor:
            if record['dish'] != item['dish']:
                not_found = True
        if not_found:
            item['date'] = item['date'] + timedelta(weeks=1)
            insert = True
    else:
        insert = True

    if insert:
        try:
            collection.insert(dict(item))
        except pymongo.errors.DuplicateKeyError:
            pass


def create_mongodb_backup():
    """
    Creates a backup for the lunch collection, it is like calling the below command at the shell:
    mongoexport -h  localhost -p  27017 -d  coolinarius -c  lunch -o  lunch_backup.json
    """
    call(["mongoexport",
          "-h", settings['MONGODB_SERVER'], "-d", settings['MONGODB_DB'], "-c", settings['MONGODB_COLLECTION'],
          "-o", settings['MONGODB_COLLECTION_BACKUP'] + '-' + str(datetime.now()).replace(' ', '-')])


def drop_collection():
    create_mongodb_backup()
    command = "db." + settings['MONGODB_DB'] + ".drop()"
    print("[COOL] Executing command: \n[COOL] %s" % command)
    call(["mongo", settings['MONGODB_DB'], "--eval", command])


def create_collection():
    # db.lunch.createIndex( { date: 1, location: 1, business: 1 , dish: 1}, { unique: true } )
    drop_collection()
    command = "db." + settings['MONGODB_COLLECTION'] + \
              '.createIndex( { date: 1, location: 1, business: 1 , dish: 1}, { unique: true } )'
    print("[COOL] Executing command: \n[COOL] %s" % command)
    call(["mongo", settings['MONGODB_DB'], "--eval", command])
