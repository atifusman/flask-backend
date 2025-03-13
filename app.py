from flask import Flask, jsonify, request
import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Load Shopify API credentials from environment variables
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_API_TOKEN = os.getenv("SHOPIFY_API_TOKEN")

@app.route('/')
def home():
    return jsonify({"message": "Welcome to my backend!"})

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"data": "This is a sample response", "status": "success"})

@app.route('/submit-review', methods=['POST'])
def submit_review():
    try:
        data = request.json
        product_id = data.get('product_id')
        review = {
            "rating": data.get('rating'),
            "comment": data.get('comment'),
            "customer": data.get('customer')
        }

        headers = {
            "X-Shopify-Access-Token": SHOPIFY_API_TOKEN,
            "Content-Type": "application/json"
        }
        metafield_url = f"{SHOPIFY_STORE_URL}/products/{product_id}/metafields.json"
        response = requests.get(metafield_url, headers=headers)
        response.raise_for_status()
        metafields = response.json().get('metafields', [])

        reviews = []
        for metafield in metafields:
            if metafield['namespace'] == 'reviews' and metafield['key'] == 'product_reviews':
                reviews = json.loads(metafield['value'])
                break

        reviews.append(review)

        payload = {
            "metafield": {
                "namespace": "reviews",
                "key": "product_reviews",
                "value": json.dumps(reviews),
                "type": "json",
                "owner_id": product_id,
                "owner_resource": "product"
            }
        }
        if any(m['namespace'] == 'reviews' and m['key'] == 'product_reviews' for m in metafields):
            metafield_id = next(m['id'] for m in metafields if m['namespace'] == 'reviews' and m['key'] == 'product_reviews')
            requests.put(f"{metafield_url}/{metafield_id}", json=payload, headers=headers)
        else:
            requests.post(metafield_url, json=payload, headers=headers)

        return jsonify({"status": "success", "message": "Review submitted!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
