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

COORDINATES = {
    'Albert': [(52.431487, 13.536813)],
    'Cafe Campus': [(52.435699, 13.529591)],
    'Esswirtschaft': [(52.431405, 13.532730), (52.427510, 13.545404), (52.499909, 13.454978)],
    'La Petite': [(52.429979, 13.541673)],
    'Sonnenschein': [(52.429812, 13.537330)],
    'Suppencult': [(52.535917, 13.422788)],
    'Die Loeffelei': [(52.502667, 13.365823)],
    'Joseph Rot Diele': [(52.502589, 13.365569)]
}
connection = pymongo.MongoClient(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
database = connection[settings['MONGODB_DB']]
collection = database[settings['MONGODB_COLLECTION']]


def print_coordinates(dst):
    obj = dumps(COORDINATES)
    with open(dst, "w") as fp:
        fp.write('const coordinatesAux = \'')
        fp.write(obj)
        fp.write('\';\nconst coordinates = JSON.parse(coordinatesAux);\n')
        fp.write('export default products;\n')


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


def export_lunches():
    """
    Creates a backup for the lunch collection, it is like calling the below command at the shell:
    mongoexport -h  localhost -p  27017 -d  coolinarius -c  lunch -o  lunch_backup.json
    """
    call(["mongoexport",
          "-h", settings['MONGODB_SERVER'], "-d", settings['MONGODB_DB'], "-c", settings['MONGODB_COLLECTION'],
          "-o", settings['MONGODB_COLLECTION_BACKUP'] + '-' + str(datetime.now()).replace(' ', '-')])


def import_lunches(filename):
    """
    Import the filename in to the lunch collection.
    mongoimport -h  localhost -p 27017 -d  coolinarius -c lunch -file filename
    :param filename: the file to import
    """
    call(["mongoimport",
          "-h", settings['MONGODB_SERVER'], "-d", settings['MONGODB_DB'], "-c", settings['MONGODB_COLLECTION'],
          "--file", filename])


def drop_collection():
    export_lunches()
    command = "db." + settings['MONGODB_COLLECTION'] + ".drop()"
    print("[COOL] Executing command: \n[COOL] %s" % command)
    call(["mongo", settings['MONGODB_DB'], "--eval", command])


def create_collection():
    # db.lunch.createIndex( { date: 1, location: 1, business: 1 , dish: 1}, { unique: true } )
    drop_collection()
    command = "db." + settings['MONGODB_COLLECTION'] + \
              '.createIndex( { date: 1, location: 1, business: 1 , dish: 1}, { unique: true } )'
    print("[COOL] Executing command: \n[COOL] %s" % command)
    call(["mongo", settings['MONGODB_DB'], "--eval", command])
