from services.db import get_db
from datetime import datetime
from bson.objectid import ObjectId


db = get_db()
properties = db.properties


# Create indexes for performance
properties.create_index("city")
properties.create_index("price")
properties.create_index("bedrooms")

# Compound index for common search pattern
properties.create_index([("city", 1), ("price", 1)])


# ---------- CREATE ----------
def create_property(data):
    property_doc = {
        "title": data["title"],
        "price": data["price"],
        "city": data["city"],
        "bedrooms": data.get("bedrooms", 0),
        "bathrooms": data.get("bathrooms", 0),
        "area_sqft": data.get("area_sqft"),
        "listed_by": data.get("listed_by"),
        "created_at": datetime.utcnow()
    }

    result = properties.insert_one(property_doc)
    return str(result.inserted_id)


def city_market_stats(city):
    pipeline = [
        {"$match": {"city": city}},
        {
            "$group": {
                "_id": "$city",
                "avgPrice": {"$avg": "$price"},
                "minPrice": {"$min": "$price"},
                "maxPrice": {"$max": "$price"},
                "totalListings": {"$sum": 1}
            }
        }
    ]

    result = list(properties.aggregate(pipeline))
    return result


def recommend_properties(city, max_price, bedrooms):
    pipeline = [
        {
            "$match": {
                "city": city,
                "price": {"$lte": int(max_price)},
                "bedrooms": int(bedrooms)
            }
        },
        {
            "$sort": {"price": 1}
        },
        {
            "$limit": 5
        },
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "price": 1,
                "bedrooms": 1,
                "city": 1
            }
        }
    ]

    return list(properties.aggregate(pipeline))


def city_overview():
    pipeline = [
        {
            "$group": {
                "_id": "$city",
                "avgPrice": {"$avg": "$price"},
                "totalListings": {"$sum": 1}
            }
        },
        {
            "$sort": {"avgPrice": 1}
        }
    ]

    return list(properties.aggregate(pipeline))


def price_by_bedrooms():
    pipeline = [
        {
            "$group": {
                "_id": "$bedrooms",
                "avgPrice": {"$avg": "$price"},
                "minPrice": {"$min": "$price"},
                "maxPrice": {"$max": "$price"},
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]

    return list(properties.aggregate(pipeline))


def cheapest_segment(city):
    pipeline = [
        {"$match": {"city": city}},
        {
            "$group": {
                "_id": "$bedrooms",
                "avgPrice": {"$avg": "$price"},
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"avgPrice": 1}},
        {"$limit": 1},
        {
            "$project": {
                "_id": 0,
                "bedrooms": "$_id",
                "avgPrice": 1,
                "count": 1
            }
        }
    ]

    return list(properties.aggregate(pipeline))


# ---------- READ ----------
def get_property_by_id(pid):
    prop = properties.find_one({"_id": ObjectId(pid)})
    if prop:
        prop["_id"] = str(prop["_id"])
    return prop


# ---------- SEARCH ----------
def search_properties(filters):
    query = {}

    # ---- Filters ----
    if "city" in filters:
        query["city"] = filters["city"]

    # price range support
    if "minPrice" in filters or "maxPrice" in filters:
        query["price"] = {}

        if "minPrice" in filters:
            query["price"]["$gte"] = int(filters["minPrice"])

        if "maxPrice" in filters:
            query["price"]["$lte"] = int(filters["maxPrice"])

    # ---- Pagination ----
    page = int(filters.get("page", 1))
    limit = int(filters.get("limit", 5))
    skip = (page - 1) * limit

    # ---- Sorting ----
    sort_field = filters.get("sortBy", "price")
    order = filters.get("order", "asc")

    sort_order = 1 if order == "asc" else -1

    cursor = (
        properties.find(query)
        .sort(sort_field, sort_order)
        .skip(skip)
        .limit(limit)
    )

    # ---- Formatting ----
    results = []
    for p in cursor:
        p["_id"] = str(p["_id"])
        results.append(p)

    return results


# ---------- UPDATE ----------
def update_property(pid, updates):
    result = properties.update_one(
        {"_id": ObjectId(pid)},
        {"$set": updates}
    )

    return result.modified_count


# ---------- DELETE ----------
def delete_property(pid):
    return properties.delete_one({"_id": ObjectId(pid)})