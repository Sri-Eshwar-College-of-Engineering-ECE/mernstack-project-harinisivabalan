from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import joblib

model = joblib.load("model.pkl")

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATABASE = "database.db"

# -----------------------
# Create Database
# -----------------------

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        stock INTEGER,
        price REAL,
        seller TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -----------------------
# Home Route
# -----------------------

@app.route("/")
def home():
    return render_template("landing.html")

# -----------------------
# Signup
# -----------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      (username, password, role))
            conn.commit()
        except:
            return "Username already exists!"

        conn.close()
        return redirect("/login")

    return render_template("signup.html")

# -----------------------
# Login
# -----------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = user[1]
            session["role"] = user[3]

            if user[3] == "admin":
                return redirect("/admin")
            elif user[3] == "seller":
                return redirect("/seller")
            else:
                return redirect("/customer")

        return "Invalid credentials!"

    return render_template("login.html")

# -----------------------
# Dashboards
# -----------------------

@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect("/login")

    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestRegressor
    import sqlite3

    # Count users and products
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM products")
    total_products = c.fetchone()[0]

    conn.close()

    



    # ML Simulation
    np.random.seed(42)
    days = 30
    sales = np.random.randint(20, 100, size=days)
    stock = 1000 - np.cumsum(sales)

    data = pd.DataFrame({
        "Sales": sales,
        "Stock": stock
    })

    data["Previous_Sales"] = data["Sales"].shift(1)
    data.dropna(inplace=True)

    X = data[["Previous_Sales", "Stock"]]
    y = data["Sales"]

    model = RandomForestRegressor()
    model.fit(X, y)

    current_stock = 150
    last_day_sales = data.iloc[-1]["Sales"]
    prediction = int(model.predict([[last_day_sales, current_stock]])[0])

    if prediction > current_stock:
        shortage = "⚠ Shortage Expected!"
    else:
        shortage = "✅ Stock Sufficient."

    labels = list(range(len(data)))
    sales_list = data["Sales"].tolist()

    return render_template("admin_dashboard.html",
                           total_users=total_users,
                           total_products=total_products,
                           prediction=prediction,
                           shortage=shortage,
                           labels=labels,
                           sales=sales_list)

@app.route("/seller")
def seller():
    if session.get("role") != "seller":
        return redirect("/login")

    # Fetch seller products
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id, name, stock, price FROM products WHERE seller=?",
              (session["user"],))
    products = c.fetchall()
    conn.close()

    predicted_products = []
    graph_labels = []
    graph_sales = []

    for product in products:
        product_id, name, stock, price = product

        # Simulated recent sales history (10 days)
        import numpy as np
        np.random.seed(product_id)
        recent_sales = np.random.randint(5, 25, size=10)

        last_sale = recent_sales[-1]

        # 🔥 REAL ML PREDICTION USING TRAINED MODEL
        predicted_demand = int(model.predict([[last_sale, stock]])[0])

        # Shortage classification
        if predicted_demand > stock:
            status = "CRITICAL"
        elif predicted_demand > stock * 0.7:
            status = "AT RISK"
        else:
            status = "SAFE"

        predicted_products.append(
            (name, stock, price, predicted_demand, status)
        )

        # Use first product for graph visualization
        graph_labels = list(range(1, len(recent_sales) + 1))
        graph_sales = recent_sales.tolist()

    return render_template("seller_dashboard.html",
                           products=predicted_products,
                           labels=graph_labels,
                           sales=graph_sales)

@app.route("/customer")
def customer():
    if session.get("role") != "customer":
        return redirect("/login")

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT name, stock, price FROM products")
    products = c.fetchall()
    conn.close()

    return render_template("customer_dashboard.html", products=products)

# -----------------------
# Logout
# -----------------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# -----------------------
# Run App
# -----------------------

@app.route("/add_product", methods=["POST"])
def add_product():
    if session.get("role") != "seller":
        return redirect("/login")

    name = request.form["name"]
    stock = request.form["stock"]
    price = request.form["price"]

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO products (name, stock, price, seller) VALUES (?, ?, ?, ?)",
              (name, stock, price, session["user"]))
    conn.commit()
    conn.close()

    return redirect("/seller")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)