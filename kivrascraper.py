from pymongo import MongoClient

import requests

# Fetch your bearer token by logging in to kivra with bankID
# Enter it manually below
BEARER_TOKEN = "<TOKEN>"

# Find this on any call done in kivra when logged in
X_ACTOR_KEY = "<ACTOR_KEY>"

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json",
    "x-actor-key": f"{X_ACTOR_KEY}"
}

# GraphQL query to fetch receipts, limit and offset can be modified
payload = {
    "operationName": "Receipts",
    "query": "query Receipts($search: String, $limit: Int, $offset: Int) {\n  receiptsV2(search: $search, limit: $limit, offset: $offset) {\n    __typename\n    total\n    offset\n    limit\n    list {\n      ...baseDetailsFields\n    }\n  }\n}\n\nfragment baseDetailsFields on ReceiptBaseDetails {\n  __typename\n  key\n  purchaseDate\n  totalAmount {\n    formatted\n  }\n  attributes {\n    isCopy\n    isExpensed\n    isReturn\n    isTrashed\n  }\n  store {\n    name\n    logo {\n      publicUrl\n    }\n  }\n  attachments {\n    id\n    type\n    name\n  }\n  accessInfo {\n    owner {\n      isMe\n      name\n    }\n  }\n}",
    "variables":
        {
            "limit": 100,
            "offset": 0,
        }
}

# MongoDb credentials and setup
client = MongoClient("mongodb://localhost:27017/")
db = client["kvittoanalys"]
collection = db["receipts"]

# Call GraphQL to fetch receipts
response = requests.post("https://bff.kivra.com/graphql", json=payload, headers=headers)
data = response.json()




print(data)
receipts = data["data"]["receiptsV2"]["list"]

# GET each receipt
for receipt in receipts:
    sleep(2)
    key = receipt["key"]
    get_url = f"https://app.api.kivra.com/v1/receipts/{key}"
    get_response = requests.get(get_url, headers=headers)
    if get_response.ok:
        receipt_data = get_response.json()
        print(f"Kvitto {key}:")
        print(receipt_data)
        collection.insert_one(receipt_data)
    else:
        print(f"Fel vid hämtning av kvitto {key}: {get_response.status_code}")
