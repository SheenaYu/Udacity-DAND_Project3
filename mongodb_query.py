"""
MongoDB queries to get statistics of the dallas map dataset
"""

db_name = "OpenStreetMaps"


def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def top_users():
    # Top 10 contributing users
    group = {"$group" : {'_id' : '$created.user', 'count' : {'$sum' : 1}}}
    sort = {"$sort" : {'count' : -1}}
    limit = {"$limit" : 10}
    pipeline = [group, sort, limit]
    return pipeline

def top_amenities():
    # Top 10 appearing amenities
    match = {"$match":{"amenity":{"$exists":1}}}
    group = {"$group":{"_id":"$amenity", "count":{"$sum":1}}}
    sort = {"$sort":{"count":-1}}
    limit = {"$limit":10}
    pipeline = [match, group, sort, limit]
    return pipeline

def top_cfccs():
    # Top10 appearing "cfcc"
    match = {"$match":{"tiger.cfcc":{"$exists":1}}}
    group = {"$group":{"_id":"$tiger.cfcc", "count":{"$sum":1}}}
    sort = {"$sort":{"count":-1}}
    limit = {"$limit":10}
    pipeline = [match, group, sort, limit]
    return pipeline

def top_fastfood():
    # Most popular fast food
    match = {"$match":{"amenity":{"$exists":1}, "amenity":"fast_food"}}
    group = {"$group":{"_id":"$cuisine", "count":{"$sum":1}}}
    sort = {"$sort":{"count":-1}}
    limit = {"$limit":1}
    pipeline = [match, group, sort, limit]
    return pipeline

def top_cities():
    # Top 10 mentioned cities
    match = {"$match":{"address.city":{"$exists":1}}}
    group = {"$group":{"_id":"$address.city", "count":{"$sum":1}}}
    sort = {"$sort":{"count":-1}}
    limit = {"$limit":10}
    pipeline = [match, group, sort, limit]
    return pipeline

def top_leisure_facilities():
    # Top 10 mentioned leisure facilities 
    match = {"$match":{"leisure":{"$exists":1}}}
    group = {"$group":{"_id":"$leisure", "count":{"$sum":1}}}
    sort = {"$sort":{"count":-1}}
    limit = {"$limit":10}
    pipeline = [match, group, sort, limit]
    return pipeline


def aggregate(db, pipeline):
    result = db.dallas.aggregate(pipeline)
    return result

def test(pipeline_function):
    db = get_db(db_name)
    pipeline = pipeline_function
    cursor = aggregate(db, pipeline)
    import pprint
    for document in cursor:
        pprint.pprint(document)

test(top_leisure_facilities())



