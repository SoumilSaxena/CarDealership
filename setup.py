from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
from functools import wraps
import hashlib
import binascii
import os
import re
app = Flask(__name__)
app.secret_key = "abc123"  # replace before project submission
conn = psycopg2.connect("dbname=postgres user=postgres password=")
cur = conn.cursor()

def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    hash_password = hashlib.pbkdf2_hmac(
        'sha512', password.encode('utf-8'), salt, 200000)
    hash_password = binascii.hexlify(hash_password)
    return (salt + hash_password).decode('ascii')


def formatPhone(num):
    num = re.sub("[ ()-]", '', num)

    if (len(num) == 10 and num.isnumeric()):
        return num[:3] + "-" + num[3:6] + "-" + num[6:]
    else:
        print(str(len(num)) + ", " + str(num.isnumeric()))
        return 0


def verify_password(stored_password, provided_password):
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    hash_password = hashlib.pbkdf2_hmac(
        'sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 200000)
    computed_stored_password = binascii.hexlify(hash_password).decode('ascii')
    return stored_password == computed_stored_password


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/employees')
def employees():
    try:
        cur.execute("SELECT * FROM Employees")
    except psycopg2.Error as e:
        print(f"\nError occured: {e}")
        return redirect(url_for('index'))
    emps = cur.fetchall()
    return render_template('employees.html', data=emps)

@app.route('/customers')
def customers():
    try:
        cur.execute("SELECT * FROM Customers")
    except psycopg2.Error as e:
        print(f"\nError occured: {e}")
        return redirect(url_for('index'))
    cust = cur.fetchall()
    return render_template('customers.html', data=cust)

@app.route('/cars')
@login_required
def cars():
    try:
        cur.execute("SELECT vin,make,color,model,year,starting_price FROM stock WHERE is_sold = false")
        data = cur.fetchall()
    except psycopg2.Error as e:
        print(f"\nError loading cars: {e}")
        return render_template('cars.html', message="An unexpected error occurred.")
    return render_template('cars.html', data=data)

@app.route('/car_filter')
@login_required
def car_filter():
    try:
        query = "SELECT vin,make,color,model,year,starting_price FROM stock WHERE 1=1"
        params = []
        if request.args['vin'] != '':
            query += " AND vin = %s"
            params.append(request.args['vin'])
        if request.args['make'] != '':
            query += " AND make = %s"
            params.append(request.args['make'])
        if request.args['color'] != '':
            query += " AND color = %s"
            params.append(request.args['color'])
        if request.args['model'] != '':
            query += " AND model = %s"
            params.append(request.args['model'])
        if request.args['year'] != '':
            query += " AND year = %s"
            params.append(request.args['year'])
        if request.args['price_low'] != '':
            query += " AND starting_price >= %s"
            params.append(request.args['price_low'])
        if request.args['price_high'] != '':
            query += " AND starting_price <= %s"
            params.append(request.args['price_high'])
        if 'sold' not in request.args:
            query += " AND is_sold = false"
        cur.execute(query, params)
        data = cur.fetchall()
    except psycopg2.Error as e:
        print(f"\nError loading cars in: {e}")
        return render_template('cars.html', message="An unexpected error occurred.")
    return render_template('cars.html', data=data)

@app.route('/menu')
def menu():
    if request.method == 'POST':
        option = request.form['option']
        if option == '1':
            return redirect(url_for('add_car'))
            # print("1. Add a car to inventory") #dealer
        elif option == '2':
            return redirect(url_for('add_customer'))
            # print("2. Add a customer") #dealer
        elif option == '3':
            return redirect(url_for('add_employee'))
            # print("3. Add an employee") #admin
        elif option == '4':
            return redirect(url_for('add_sale'))
            # print("4. Record a sale") #dealer
        elif option == '5':
            return redirect(url_for('main'))
            # print("5. Log out")
    else:
        options = [
            {'text': '1. Add a car to inventory', 'url': url_for('add_car')},
            {'text': '2. Add a customer', 'url': url_for('add_customer')},
            {'text': '3. Add an employee', 'url': url_for('add_employee')},
            {'text': '4. Record a sale', 'url': url_for('add_sale')},
            {'text': '5. Log out', 'url': url_for('main')}
        ]
        return render_template('menu.htl', options=options)
    data = cur.fetchall()
    return render_template('cars.html', data=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if 'logged_in' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # query for info of entered user, including hashed password
        try:
            cur.execute(
                "SELECT user_id,password,level FROM users WHERE username = %s", (username,))
        except psycopg2.Error as e:
            print(f"\nError selecting password in: {e}")
            return "Error"

        cur_user = cur.fetchone()

        # hash inputted passsword and check against query result
        if cur_user:
            stored_database_password = cur_user[1]
            if verify_password(stored_database_password, password):
                session['logged_in'] = True
                session['user_id'] = cur_user[0]
                session['level'] = cur_user[2]
                print("Password Verified")
                return redirect(url_for('index'))
        message = "Incorrect username or password"
    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('level', None)
    return redirect(url_for('login'))


@app.route('/add_sale', methods=['GET', 'POST'])
@login_required
def add_sale():
    if request.method == 'POST':
        vin = request.form['vin']
        custID = request.form['Customer ID']
        price = request.form['Selling price']
        dealer = request.form['Dealer']
        loc = request.form['Location']

        # level = session.get('level')
        # if level not in [0, 1, 2]:
        #     return "You don't have permission to add cars."

        cur.execute("INSERT INTO Sales(vin, customer_ID, selling_price, dealer, location) VALUES (%s, %s, %s,%s,%s)",
                    (vin, custID, price, dealer, loc))
        conn.commit()
        print("Sale recorded!")
        return redirect(url_for('index'))

    return render_template('add_sale.html')


@app.route('/add_car', methods=['GET', 'POST'])
@login_required
def add_car():
    if request.method == 'POST':
        vin = request.form['vin']
        make = request.form['make']
        color = request.form['color']
        model = request.form['model']
        year = request.form['year']
        starting_price = request.form['starting_price']

        level = session.get('level')
        if level not in [0, 1, 2]:
            return "You don't have permission to add cars."
        try:
            cur.execute("INSERT INTO stock(vin, make, color, model, year, starting_price, is_sold) VALUES (%s, %s, %s,%s,%s,%s,%s)",
                        (vin, make, color, model, year, starting_price, False))
            conn.commit()
        except psycopg2.Error as e:
            print("Error creating account: {e}")
    return redirect(url_for('cars'))


@app.route('/add_employee', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birthdate = request.form['birthdate']
        address = request.form['address']
        salary = request.form['salary']
        level = request.form['level']
        password = hash_password(password)  # Password gets hashed

        # Check if username or password already exists
        cur.execute(
            "SELECT user_id FROM Users WHERE username = %s", (username,))
        existing_user = cur.fetchone()
        if existing_user:
            return render_template('add_employee.html', message="Username already exists.")

        try:
            cur.execute("INSERT INTO Users (username, password, level) VALUES (%s, %s, %s) RETURNING user_id",
                        (username, password, level))
            user_id = cur.fetchone()[0]
            cur.execute("INSERT INTO employees(user_id, first_name, last_name, Birthdate, salary, address, role_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (user_id, first_name, last_name, birthdate, salary, address, level))
            conn.commit()
            return redirect(url_for('index'))
        except psycopg2.Error as e:
            return f"Error creating account: {e}"
    else:
        return render_template('add_employee.html')


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if 'logged_in' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        # All accounts have customer permissions by default. Employees should contact admin.
        level = 3
        password = hash_password(password)  # Password gets hashed

        # Check if username or password already exists
        cur.execute(
            "SELECT user_id FROM Users WHERE username = %s", (username,))
        existing_user = cur.fetchone()
        if existing_user:
            return render_template('create_account.html', message="Username or password already exists.")

        try:
            cur.execute("INSERT INTO Users (username, password, level) VALUES (%s, %s, %s) RETURNING user_id",
                        (username, password, level))
            session['user_id'] = cur.fetchone()[0]
            cur.execute("INSERT INTO Customers(user_id, first_name, last_name, phone_number, email_address) VALUES (%s, %s, %s, %s, %s)",
                        (session['user_id'], first_name, last_name, phone_number, email))
            conn.commit()
            session['logged_in'] = True
            session['level'] = level
            return redirect(url_for('index'))
        except psycopg2.Error as e:
            return f"Error creating account: {e}"
    else:
        return render_template('create_account.html')


if __name__ == '__main__':
    app.run(debug=True)
