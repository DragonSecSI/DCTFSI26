import pickle
import base64
from flask import Flask, render_template, request, redirect, url_for, make_response

app = Flask(__name__)

PRODUCTS = {
    1: {"name": "Strawberry Jam", "price": 3.50, "emoji": "🍓", "desc": "Made from grandma's garden strawberries, picked at sunrise."},
    2: {"name": "Apricot Jam",    "price": 3.00, "emoji": "🍑", "desc": "Sweet summer apricots, slow-cooked with love."},
    3: {"name": "Plum Jam",       "price": 3.20, "emoji": "🍑", "desc": "Old recipe from great-grandma, tangy and rich."},
    4: {"name": "Apple Kompot",   "price": 2.50, "emoji": "🍎", "desc": "Cloudy apple kompot, best served cold."},
    5: {"name": "Cherry Kompot",  "price": 2.80, "emoji": "🍒", "desc": "Deep red cherries, just a hint of clove."},
    6: {"name": "Pear Kompot",    "price": 2.60, "emoji": "🍐", "desc": "Delicate pear, light and refreshing."},
}


def get_cart():
    raw = request.cookies.get("cart")
    if not raw:
        return {}
    try:
        data = base64.b64decode(raw)
        cart = pickle.loads(data)
        if not isinstance(cart, dict):
            return {}
        return cart
    except Exception:
        return {}


def set_cart(response, cart):
    data = pickle.dumps(cart)
    encoded = base64.b64encode(data).decode()
    response.set_cookie("cart", encoded)
    return response


@app.route("/")
def index():
    cart = get_cart()
    count = sum(cart.values()) if cart else 0
    return render_template("index.html", products=PRODUCTS, cart_count=count)


@app.route("/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    if product_id not in PRODUCTS:
        return redirect(url_for("index"))
    cart = get_cart()
    cart[product_id] = cart.get(product_id, 0) + 1
    resp = make_response(redirect(url_for("index")))
    return set_cart(resp, cart)


@app.route("/cart")
def view_cart():
    cart = get_cart()
    items = []
    total = 0.0
    for pid, qty in cart.items():
        if pid in PRODUCTS:
            p = PRODUCTS[pid]
            subtotal = p["price"] * qty
            total += subtotal
            items.append({"product": p, "qty": qty, "subtotal": subtotal})
    return render_template("cart.html", items=items, total=total)


@app.route("/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = get_cart()
    cart.pop(product_id, None)
    resp = make_response(redirect(url_for("view_cart")))
    return set_cart(resp, cart)


@app.route("/checkout", methods=["POST"])
def checkout():
    cart = get_cart()
    if not cart:
        return redirect(url_for("index"))

    name    = request.form.get("name", "").strip()
    phone   = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()
    notes   = request.form.get("notes", "").strip()

    # Build order summary for the confirmation page
    items = []
    total = 0.0
    for pid, qty in cart.items():
        if pid in PRODUCTS:
            p = PRODUCTS[pid]
            subtotal = p["price"] * qty
            total += subtotal
            items.append({"product": p, "qty": qty, "subtotal": subtotal})

    resp = make_response(render_template(
        "thanks.html",
        name=name,
        phone=phone,
        address=address,
        notes=notes,
        items=items,
        total=total,
    ))
    resp.set_cookie("cart", "", expires=0)
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
