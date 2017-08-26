import pymongo
from bson.json_util import dumps
from scrapy.conf import settings
from mahlzeit.date_utils import get_today_midnight
from mahlzeit.date_utils import get_date_of_weekday
from mahlzeit.date_utils import get_current_day_week_number
from mahlzeit.date_utils import get_current_weekday_number


client = pymongo.MongoClient('localhost', 27017)
connection = pymongo.MongoClient(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
db = connection[settings['MONGODB_DB']]
collection = db[settings['MONGODB_COLLECTION']]


def print_cursor_to_file(cursor, dst, variable=False):
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


def get_current_week_lunches_mongodb(list_business=None, weekday_start=None):
    # calculate start and finish date
    if not weekday_start:
        start_date = get_today_midnight()
    else:
        start_date = get_date_of_weekday('monday')
    finish_date = get_date_of_weekday('friday')
    # perform query
    if list_business:
        result = dict()
        for business in list_business:
            result[business] = collection.find({"business": business,
                                                "date": {"$gte": start_date, "$lte": finish_date}})
    else:
        result = collection.find({"date": {"$gte": start_date, "$lte": finish_date}})
    return result


def insert_mongodb(item):
    list_business = list()
    list_business.append(item['business'])
    records = get_current_week_lunches_mongodb(list_business)
    counts = count_lunches(records, list_business)
    current_week = get_current_day_week_number()

    # item is from current week and db has already items for this week
    if counts[item['business']] > 0 and get_current_weekday_number() > 4:
        for record in records:
            if record['dish'] != item['dish']:
                # log
                print('WRONG WEEK???')
                pass
    # item is in a future week
    elif item['date'].isocalendar()[1] > current_week:
        print('NEXT WEEK')
        pass
    else:
        try:
            collection.insert(dict(item))
        except pymongo.errors.DuplicateKeyError:
            pass



# db.lunch.createIndex( { date: 1, location: 1, business: 1 , dish: 1}, { unique: true } )
