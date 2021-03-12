import pymongo

db_client = pymongo.MongoClient("mongodb://localhost:27017")
db = db_client["gd_data_mining"]
collection = db["magnit_products"]

for p in collection.find({"promo_name": "Дари играя", "product_name": {"$regex": "[Ш|ш]околад"}}):
    print(p)
