from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
from functools import wraps
import hashlib
import binascii
import os
import re
app = Flask(__name__)
app.secret_key = "abc123"  # replace before project submission
conn = psycopg2.connect("dbname=dbdesign user=postgres password=Soumil008")
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


@app.route('/cars')
def cars():
    try:
        cur.execute(
            "SELECT vin,make,color,model,year,starting_price FROM stock WHERE is_sold = false")
    except psycopg2.Error as e:
        print(f"\nError selecting password in: {e}")
        return redirect(url_for('index'))
    data = cur.fetchall()
    return render_template('cars.html', data=data)


@app.route('/menu_dealer')
def menu_dealer():
    if request.method == 'POST':
        option = request.form['option']
        if option == '1':
            return redirect(url_for('add_car'))
            # print("1. Add a car to inventory") #dealer
        elif option == '2':
            return redirect(url_for('add_customer'))
            # print("2. Add a customer") #dealer
        elif option == '3':
            return redirect(url_for('add_sale'))
            # print("4. Record a sale") #dealer
        elif option == '4':
            return redirect(url_for('list_car_options'))
            # List cars
        elif option == '5':
            return redirect(url_for('list_employees'))
            # List employees
        elif option == '6':
            return redirect(url_for('list_customers'))
            # List customers
        elif option == '7':
            return redirect(url_for('list_sales'))
            # List sales
        elif option == '8':
            return redirect(url_for('main'))
            # Return to home screen
    else:
        options = [
            {'text': '1. Add a car to inventory', 'url': url_for('add_car')},
            {'text': '2. Add a customer', 'url': url_for('add_customer')},
            {'text': '3. Record a sale', 'url': url_for('add_sale')},
            {'text': '4. List the cars in stock',
                'url': url_for('list_car_options')},
            {'text': '5. List the employees',
                'url': url_for('list_employees')},
            {'text': '6. List the customers',
                'url': url_for('list_customers')},
            {'text': '7. List the sales', 'url': url_for('list_sales')},
            {'text': '8. Log out', 'url': url_for('main')}
        ]
        return render_template('menu_dealer.htl', options=options)


@app.route('/menu_admin')
def menu_admin():
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
            return redirect(url_for('remove_car'))
            # print("5. Remove a car")
        elif option == '6':
            return redirect(url_for('remove_employee'))
            # Remove an employee
        elif option == '7':
            return redirect(url_for('remove_customer'))
            # Remove a customer
        elif option == '8':
            return redirect(url_for('remove_sale'))
            # Remove a sale
        elif option == '9':
            return redirect(url_for('list_car_options'))
            # List cars
        elif option == '10':
            return redirect(url_for('list_employees'))
            # List employees
        elif option == '11':
            return redirect(url_for('list_customers'))
            # List customers
        elif option == '12':
            return redirect(url_for('list_sales'))
            # List sales
        elif option == '13':
            return redirect(url_for('main'))
            # Return to home screen
    else:
        options = [
            {'text': '1. Add a car to inventory', 'url': url_for('add_car')},
            {'text': '2. Add a customer', 'url': url_for('add_customer')},
            {'text': '3. Add an employee', 'url': url_for('add_employee')},
            {'text': '4. Record a sale', 'url': url_for('add_sale')},
            {'text': '5. Remove a car from stock',
                'url': url_for('remove_car')},
            {'text': '6. Remove an employee',
                'url': url_for('remove_employee')},
            {'text': '7. Remove a customer',
                'url': url_for('remove_customer')},
            {'text': '8. Remove a sale', 'url': url_for('remove_sale')},
            {'text': '9. List the cars in stock',
                'url': url_for('list_car_options')},
            {'text': '10. List the employees',
                'url': url_for('list_employees')},
            {'text': '11. List the customers',
                'url': url_for('list_customers')},
            {'text': '12. List the sales', 'url': url_for('list_sales')},
            {'text': '13. Log out', 'url': url_for('main')}
        ]
        return render_template('menu_admin.htl', options=options)


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


@app.route('/add_employee', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        level = request.form['level']
        model = request.form['model']
        year = request.form['year']
        starting_price = request.form['starting_price']

        level = session.get('level')
        if level not in [0, 1, 2]:
            return "You don't have permission to add cars."

        cur.execute("INSERT INTO stock(vin, make, color, model, year, starting_price, is_sold) VALUES (%s, %s, %s,%s,%s,%s,%s)",
                    (vin, make, color, model, year, starting_price, False))
        conn.commit()
        print("Car added to the database!")
        return redirect(url_for('index'))

    return render_template('add_car.html')


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

        cur.execute("INSERT INTO stock(vin, make, color, model, year, starting_price, is_sold) VALUES (%s, %s, %s,%s,%s,%s,%s)",
                    (vin, make, color, model, year, starting_price, False))
        conn.commit()
        print("Car added to the database!")
        return redirect(url_for('index'))

    return render_template('add_car.html')


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
