from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
from datetime import datetime

app = Flask(__name__)
orders_data = [
    {"id": "#ORD2341", "date": "08 Jan 2026", "product": "Sodium Hypochlorite", "qty": "250 kg", "price": "₹ 12,500", "total": "₹ 12,500", "status": "Delivered"},
    {"id": "#ORD2336", "date": "05 Jan 2026", "product": "Hydrogen Peroxide", "qty": "500 kg", "price": "₹ 27,800", "total": "₹ 27,800", "status": "Pending"},
]

app.config['SECRET_KEY'] = 'chemical-marketplace-secret'
app.config['DATABASE'] = 'C:/path/to/database.db'

# ----- LOGIN SETUP -----
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# ----- USER MODEL -----
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role


# ----- IN-MEMORY DATABASE -----
db_conn = sqlite3.connect(':memory:', check_same_thread=False)
db_conn.row_factory = sqlite3.Row


def init_db():
    cursor = db_conn.cursor()
    conn = sqlite3.connect("your_database.db")
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    cursor.execute("CREATE TABLE notifications ( id INTEGER PRIMARY KEY AUTOINCREMENT,supplier TEXT NOT NULL,message TEXT NOT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute('CREATE TABLE chemicals (id INTEGER PRIMARY KEY, name TEXT, price REAL, supplier TEXT)')
    
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('supplier1', 'pass123', 'supplier')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('supplier2', 'pass123', 'supplier')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('supplier3', 'pass123', 'supplier')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('buyer1', 'pass123', 'buyer')")
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())

    db_conn.commit()


@login_manager.user_loader
def load_user(user_id):
    user = db_conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if user:
        return User(user['id'], user['username'], user['role'])
    return None


# ----- ROUTES -----
@app.route('/')
def index():
    return render_template('welcome.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db_conn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                               (username, password)).fetchone()

        if user:
            login_user(User(user['id'], user['username'], user['role']))
            return redirect(url_for('dashboard'))
        flash('Login Failed')
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin'))
    elif current_user.role == 'supplier':
        return redirect(url_for('supplier'))
    return redirect(url_for('buyer'))


@app.route('/admin')
@login_required
def admin():
    users = db_conn.execute('SELECT * FROM users').fetchall()
    chemicals = db_conn.execute('SELECT * FROM chemicals').fetchall()
    return render_template('admin.html', users=users, chemicals=chemicals)



@app.route('/buyer')
@login_required
def buyer():
    chems = db_conn.execute('SELECT * FROM chemicals').fetchall()
    return render_template('buyer.html', chemicals=chems)



@app.route('/supplier')
@login_required
def supplier():
    chems = db_conn.execute("SELECT * FROM chemicals WHERE supplier = ?", (current_user.username,)).fetchall()
    notifications = db_conn.execute("SELECT * FROM notifications WHERE supplier = ?", (current_user.username,)).fetchall()
    return render_template('supplier.html', chemicals=chems, notifications=notifications)


@app.route('/add_to_cart/<int:chemical_id>', methods=['POST'])
@login_required
def add_to_cart(chemical_id):
    chem = db_conn.execute("SELECT * FROM chemicals WHERE id = ?", (chemical_id,)).fetchone()
    if chem:
        supplier = chem['supplier']
        message = f"Buyer {current_user.username} added {chem['name']} to cart."
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # FIX: Insert into notifications, not chemicals
        db_conn.execute(
            "INSERT INTO notifications (supplier, message, created_at) VALUES (?, ?, ?)",
            (supplier, message, time)
        )
        db_conn.commit()
    return redirect(url_for('buyer'))

@app.route('/add', methods=['POST'])
@login_required
def add_chemical():
    db_conn.execute("INSERT INTO chemicals (name, price, supplier) VALUES (?, ?, ?)",
                    (request.form['name'], request.form['price'], current_user.username))
    db_conn.commit()
    return redirect(url_for('supplier'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# ----- EXTRA PAGES -----
@app.route('/product')
def product_page():
    return render_template("product_detail.html", product=product)


@app.route('/orders')
def orders():
    return render_template("order_history.html", orders=orders_data)


@app.route('/reviews')
def reviews():
    return render_template("reviews.html", reviews=reviews_data)


# @app.route('/notifications')
# def notifications():
#     return render_template("notifications.html", notifications=notifications_data)


@app.route('/support')
def support():
    return render_template("support.html")


@app.route('/reports')
def reports():
    return render_template("reports.html", analytics=analytics_data)




# ----- EXTRA PAGE DATA -----
product = {
    "name": "Sodium Hypochlorite 12%",
    "cas": "7681-52-9",
    "category": "Water Treatment Chemical",
    "supplier": "ChemX Industries Pvt Ltd",
    "price": "₹ 52.50 / Kg",
    "specs": ["12% Concentration", "Industrial Grade", "50L / 200L Drums"]
}

orders_data = [
    {"id": "#ORD2341", "date": "08 Jan 2026", "product": "Sodium Hypochlorite", "total": "₹ 12,500", "status": "Delivered"},
    {"id": "#ORD2336", "date": "05 Jan 2026", "product": "Hydrogen Peroxide", "total": "₹ 27,800", "status": "Pending"},
]

reviews_data = [
    {"user": "Akshay", "text": "Fast payment and order handling", "rating": 4},
    {"user": "Meera", "text": "Proper packaging and good quality", "rating": 5},
]

notifications_data = [
    "Your Order #ORD2336 has been shipped",
    "New price update for Caustic Soda",
    "SDS updated for Hydrogen Peroxide",
    "Invoice available for Order #ORD2341"
]

analytics_data = {
    "orders": 240,
    "buyers": 48,
    "revenue": "₹ 3,21,000",
    "top": "Hydrogen Peroxide 50%",
    "pending": 12
}


# ----- RUN -----
if __name__ == '__main__':
    init_db()
    print(">>> SERVER RUNNING AT http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)
