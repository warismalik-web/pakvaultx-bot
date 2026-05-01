from pymongo import MongoClient
from config import MONGO_URL

client = MongoClient(MONGO_URL)
db = client["pakvaultx"]

products_col = db["products"]

def save_products(products):
    products_col.delete_many({})
    products_col.insert_many(products)

def get_products():
    return list(products_col.find())

def toggle_product(pid):
    product = products_col.find_one({"id": pid})
    if product:
        products_col.update_one(
            {"id": pid},
            {"$set": {"active": not product.get("active", True)}}
        )
