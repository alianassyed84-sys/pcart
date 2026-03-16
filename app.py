# ============================================================
#   Shopping Cart System — Python Flask Backend
#   Group 6 | BE II Semester CSE-A | A.Y 2025-2026
#   Scientific Programming Seminar | 4-4-2026
#
#   HOW TO RUN:
#   Step 1:  pip install flask flask-cors
#   Step 2:  python app.py
#   Step 3:  Open browser → http://localhost:5000
# ============================================================

import json
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# THE CART DICTIONARY & PERSISTENCE
DATA_FILE = "cart.json"
cart = {}

def load_data():
    global cart
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                cart = json.load(f)
            print(f"  [LOADED] {len(cart)} items from {DATA_FILE}")
        except Exception as e:
            print(f"  [ERROR] Loading {DATA_FILE}: {e}")
            cart = {}
    else:
        cart = {}

def save_data():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(cart, f, indent=4)
        # print(f"  [SAVED] {len(cart)} items to {DATA_FILE}")
    except Exception as e:
        print(f"  [ERROR] Saving {DATA_FILE}: {e}")

# Initial load
load_data()

# Serve the website
@app.route("/")
def home():
    return send_file("index.html")

# CONDITION 1 — Add product and price
@app.route("/cart/add", methods=["POST"])
def add_product():
    data  = request.get_json()
    name  = str(data.get("name", "")).strip()
    price = data.get("price")
    qty   = data.get("quantity", 1)
    
    if not name:
        return jsonify({"success": False, "message": "Enter product name."}), 400
    try:
        price = float(price)
        qty = int(qty)
    except:
        return jsonify({"success": False, "message": "Price and quantity must be numbers."}), 400
    
    if price < 0:
        return jsonify({"success": False, "message": "Price cannot be negative."}), 400
    if qty < 1:
        return jsonify({"success": False, "message": "Quantity must be at least 1."}), 400
        
    item_total = price * qty
    cart[name] = {"price": price, "qty": qty, "total": item_total}          # dictionary assignment
    save_data()                 # persist change
    
    # Calculate overall total
    total = round(float(sum(item["total"] for item in cart.values())), 2)
    print(f"  ADDED: '{name}' (x{qty}) = Rs.{item_total:.2f} | Total = Rs.{total}")
    return jsonify({
        "success": True,
        "message": f"'{name}' added ({qty}x) at Rs.{item_total:.2f}",
        "data": {"cart": cart.copy(), "total": total, "items": len(cart)}
    })

# CONDITION 2 — Remove product
@app.route("/cart/remove/<string:name>", methods=["DELETE"])
def remove_product(name):
    name = name.strip()
    if name not in cart:
        return jsonify({"success": False, "message": f"'{name}' not found."}), 404
    cart.pop(name, None)        # safer dictionary deletion
    save_data()                 # persist change
    
    total = round(float(sum(item["total"] for item in cart.values())), 2)
    print(f"  REMOVED: '{name}' | Total = Rs.{total}")
    return jsonify({
        "success": True,
        "message": f"'{name}' removed from cart.",
        "data": {"cart": cart.copy(), "total": total, "items": len(cart)}
    })

# CONDITION 3 — Calculate total bill
@app.route("/cart/total", methods=["GET"])
def calculate_total():
    total = sum(item["total"] for item in cart.values())
    total = round(float(total), 2)
    breakdown = [{"name": k, "price": v["price"], "qty": v["qty"], "total": v["total"]} for k, v in cart.items()]
    print(f"  TOTAL BILL: Rs.{total} | {len(cart)} item(s)")
    return jsonify({
        "success": True,
        "message": f"Total bill: Rs.{total:.2f}",
        "data": {
            "cart": cart.copy(),
            "total": total,
            "items": len(cart),
            "breakdown": breakdown
        }
    })

# EXTRA — View all items
@app.route("/cart", methods=["GET"])
def view_cart():
    # Ensure float for round()
    total = round(float(sum(item["total"] for item in cart.values())), 2)
    breakdown = [{"name": k, "price": v["price"], "qty": v["qty"], "total": v["total"]} for k, v in cart.items()]
    return jsonify({
        "success": True,
        "message": f"Cart has {len(cart)} item(s). Total: Rs.{total}",
        "data": {"cart": cart.copy(), "total": total, "items": len(cart), "breakdown": breakdown}
    })

# EXTRA — Clear cart
@app.route("/cart/clear", methods=["DELETE"])
def clear_cart():
    count = len(cart)
    cart.clear()
    save_data()                 # persist change
    print(f"  CART CLEARED — {count} item(s) removed.")
    return jsonify({
        "success": True,
        "message": f"Cart cleared. {count} item(s) removed.",
        "data": {"cart": {}, "total": 0.0, "items": 0}
    })

if __name__ == "__main__":
    print()
    print("=" * 54)
    print("   Shopping Cart System  —  Group 6")
    print("   BE II Semester CSE-A  |  4-4-2026")
    print("=" * 54)
    print()
    print("   CONDITION 1  →  POST   /cart/add")
    print("   CONDITION 2  →  DELETE /cart/remove/<n>")
    print("   CONDITION 3  →  GET    /cart/total")
    print()
    print("   Open browser:  http://localhost:5000")
    print()
    app.run(debug=True, host="0.0.0.0", port=5000)
