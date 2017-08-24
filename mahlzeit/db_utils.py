from pymongo import MongoClient
from bson.json_util import dumps
from mahlzeit.date_utils import get_today_midnight
from mahlzeit.date_utils import get_date_of_weekday


client = MongoClient('localhost', 27017)


def count_lunches(list_business=None, start=None):
    lunches = get_week_lunches_mongodb(list_business, start)
    if isinstance(lunches, dict):
        result = dict()
        for key, cursor in lunches.items():
            result[key] = cursor.count()
    else:
        result = lunches.count()
    return result


def get_week_lunches_mongodb(list_business=None, start=None):
    collection = client.coolinarius.lunch
    # calculate start and finish date
    if not start:
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


# db.lunch.createIndex( { date: 1, location: 1, business: 1 , dish: 1}, { unique: true } )
