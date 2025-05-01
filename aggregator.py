from datetime import datetime

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["kvittoanalys"]
collection = db["receipts"]


start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 5, 1)

pipeline = [
    {
        "$match": {
            "receipt.business_unit.name": {"$regex": "ICA", "$options": "i"},
            "receipt.time_of_purchase": {
                "$gte": start_date,
                "$lt": end_date
            }
        }
    },
    {"$unwind": "$receipt.items"},
    {
        "$set": {
            "cleaned_description": {
                "$replaceAll": {
                    "input": "$receipt.items.description",
                    "find": "*",
                    "replacement": ""
                }
            }
        }
    },
    {
        "$group": {
            "_id": "$cleaned_description",
            "total_spent": {"$sum": "$receipt.items.extended_gross_amount"},
            "quantity_bought": {"$sum": "$receipt.items.quantity.value"},
            "count": {"$sum": 1}
        }
    },
    {"$sort": {"total_spent": -1}}
]


results = list(collection.aggregate(pipeline))

for item in results:
    print(f"{item['_id']}: {item['quantity_bought']} st – {item['total_spent']:.2f} kr ({item['count']} köp)")
