
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def connect():
    return sqlite3.connect("shop.db")


def create_database():
    con = connect()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price REAL,
        description TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        product_id INTEGER,
        quantity INTEGER
    )
    """)

    cur.execute("SELECT COUNT(*) FROM products")

    if cur.fetchone()[0] == 0:
        products = [
            ("Notebook", 50, "A school notebook"),
            ("Pen", 10, "A blue ink pen"),
            ("School Bag", 650, "A school bag"),
            ("Water Bottle", 150, "A water bottle"),
            ("Pencil Box", 100, "A pencil box")
        ]

        cur.executemany(
            "INSERT INTO products (name, price, description) VALUES (?, ?, ?)",
            products
        )

    con.commit()
    con.close()


@app.route("/")
def home():
    con = connect()
    cur = con.cursor()

    cur.execute("SELECT * FROM products")
    products = cur.fetchall()

    con.close()

    return render_template("home.html", products=products)


@app.route("/product/<int:id>")
def product(id):
    con = connect()
    cur = con.cursor()

    cur.execute("SELECT * FROM products WHERE id=?", (id,))
    product = cur.fetchone()

    con.close()

    if product is None:
        return "Product not found!"

    return render_template("product.html", product=product)


@app.route("/order/<int:id>", methods=["GET", "POST"])
def order(id):
    con = connect()
    cur = con.cursor()

    cur.execute("SELECT * FROM products WHERE id=?", (id,))
    product = cur.fetchone()

    if product is None:
        con.close()
        return "Product not found!"

    if request.method == "POST":
        name = request.form["name"].strip()
        quantity = request.form["quantity"]

        if name == "":
            con.close()
            return "Please enter your name!"

        try:
            quantity = int(quantity)

            if quantity <= 0:
                con.close()
                return "Quantity must be positive!"

        except ValueError:
            con.close()
            return "Enter a valid quantity!"

        cur.execute(
            "INSERT INTO orders (customer_name, product_id, quantity) VALUES (?, ?, ?)",
            (name, id, quantity)
        )

        order_id = cur.lastrowid

        con.commit()
        con.close()

        return redirect(url_for("confirmation", id=order_id))

    con.close()

    return render_template("order.html", product=product)


@app.route("/confirmation/<int:id>")
def confirmation(id):
    con = connect()
    cur = con.cursor()

    cur.execute("""
    SELECT orders.id, orders.customer_name,
    products.name, orders.quantity, products.price
    FROM orders
    JOIN products ON orders.product_id = products.id
    WHERE orders.id=?
    """, (id,))

    order = cur.fetchone()

    con.close()

    if order is None:
        return "Order not found!"

    total = order[3] * order[4]

    return render_template(
        "confirmation.html",
        order=order,
        total=total
    )


if __name__ == "__main__":
    create_database()
    app.run(debug=True)
