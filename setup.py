from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import hashlib
import binascii
import os
import re
app = Flask(__name__)
app.secret_key = "abc123" # replace before project submission
conn = psycopg2.connect("dbname=postgres user=postgres password=5E#asOL32")
cur = conn.cursor()


def hash_password(password):
    salt = hashlib.sha256(os.urandom(16)).hexdigest().encode('ascii')
    hashed_password = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt, 100000)
    hashed_password = binascii.hexlify(hashed_password).decode('ascii')
    hashed_password = salt.decode('ascii') + hashed_password
    return hashed_password


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
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/view_cars')
def view_cars():
    return "View Cars"

@app.route('/menu_dealer')
def menu_dealer():
    if request.method == 'POST':
        option = request.form['option']
        if option == '1':
            return redirect(url_for('add_car'))
            #print("1. Add a car to inventory") #dealer
        elif option == '2':
            return redirect(url_for('add_customer'))
            #print("2. Add a customer") #dealer
        elif option == '3':
            return redirect(url_for('add_sale'))
            #print("4. Record a sale") #dealer
        elif option == '4':
            return redirect(url_for('list_car_options'))
            #List cars
        elif option == '5':
            return redirect(url_for('list_employees'))
            #List employees
        elif option == '6':
            return redirect(url_for('list_customers'))
            #List customers
        elif option == '7':
            return redirect(url_for('list_sales'))
            #List sales
        elif option == '8':
            return redirect(url_for('main'))
            #Return to home screen
    else:
        options = [
            {'text': '1. Add a car to inventory', 'url': url_for('add_car')},
            {'text': '2. Add a customer', 'url': url_for('add_customer')},
            {'text': '3. Record a sale', 'url': url_for('add_sale')},
            {'text': '4. List the cars in stock', 'url': url_for('list_car_options')},
            {'text': '5. List the employees', 'url': url_for('list_employees')},
            {'text': '6. List the customers', 'url': url_for('list_customers')},
            {'text': '7. List the sales', 'url': url_for('list_sales')},
            {'text': '8. Log out', 'url': url_for('main')}
        ]
        return render_template('menu_dealer.htl', options = options)

@app.route('/menu_admin')
def menu_admin():
    if request.method == 'POST':
        option = request.form['option']
        if option == '1':
            return redirect(url_for('add_car'))
            #print("1. Add a car to inventory") #dealer
        elif option == '2':
            return redirect(url_for('add_customer'))
            #print("2. Add a customer") #dealer
        elif option == '3':
            return redirect(url_for('add_employee'))
            #print("3. Add an employee") #admin
        elif option == '4':
            return redirect(url_for('add_sale'))
            #print("4. Record a sale") #dealer
        elif option == '5':
            return redirect(url_for('remove_car'))
            #print("5. Remove a car") 
        elif option == '6':
            return redirect(url_for('remove_employee'))
            #Remove an employee
        elif option == '7':
            return redirect(url_for('remove_customer'))
            #Remove a customer
        elif option == '8':
            return redirect(url_for('remove_sale'))
            #Remove a sale
        elif option == '9':
            return redirect(url_for('list_car_options'))
            #List cars
        elif option == '10':
            return redirect(url_for('list_employees'))
            #List employees
        elif option == '11':
            return redirect(url_for('list_customers'))
            #List customers
        elif option == '12':
            return redirect(url_for('list_sales'))
            #List sales
        elif option == '13':
            return redirect(url_for('main'))
            #Return to home screen
    else:
        options = [
            {'text': '1. Add a car to inventory', 'url': url_for('add_car')},
            {'text': '2. Add a customer', 'url': url_for('add_customer')},
            {'text': '3. Add an employee', 'url': url_for('add_employee')},
            {'text': '4. Record a sale', 'url': url_for('add_sale')},
            {'text': '5. Remove a car from stock', 'url': url_for('remove_car')},
            {'text': '6. Remove an employee', 'url': url_for('remove_employee')},
            {'text': '7. Remove a customer', 'url': url_for('remove_customer')},
            {'text': '8. Remove a sale', 'url': url_for('remove_sale')},
            {'text': '9. List the cars in stock', 'url': url_for('list_car_options')},
            {'text': '10. List the employees', 'url': url_for('list_employees')},
            {'text': '11. List the customers', 'url': url_for('list_customers')},
            {'text': '12. List the sales', 'url': url_for('list_sales')},
            {'text': '13. Log out', 'url': url_for('main')}
        ]
        return render_template('menu_admin.htl', options = options)
@app.route('/menu')
def menu():
    if request.method == 'POST':
        option = request.form['option']
        if option == '1':
            return redirect(url_for('add_car'))
            #print("1. Add a car to inventory") #dealer
        elif option == '2':
            return redirect(url_for('add_customer'))
            #print("2. Add a customer") #dealer
        elif option == '3':
            return redirect(url_for('add_employee'))
            #print("3. Add an employee") #admin
        elif option == '4':
            return redirect(url_for('add_sale'))
            #print("4. Record a sale") #dealer
        elif option == '5':
            return redirect(url_for('main'))
            #print("5. Log out")
    else:
        options = [
            {'text': '1. Add a car to inventory', 'url': url_for('add_car')},
            {'text': '2. Add a customer', 'url': url_for('add_customer')},
            {'text': '3. Add an employee', 'url': url_for('add_employee')},
            {'text': '4. Record a sale', 'url': url_for('add_sale')},
            {'text': '5. Log out', 'url': url_for('main')}
        ]
        return render_template('menu.htl', options = options)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # query for info of entered user, including hashed password
        try:
            cur.execute("SELECT user_id,password,level FROM users WHERE username = %s", (username,))
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
                return render_template('index.html')
        message = "Incorrect username or password"
    return render_template('login.html', message = message)


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        level = request.form['level']
        password = hash_password(password)  # Password gets hashed

        # Check if username or password already exists
        cur.execute(
            "SELECT user_id FROM Users WHERE username = %s OR password = %s", (username, password))
        existing_user = cur.fetchone()
        if existing_user:
            return "Error creating account: Username or password already exists."

        try:
            cur.execute("INSERT INTO Users (username, password, level) VALUES (%s, %s, %s) RETURNING user_id",
                        (username, password, level))
            conn.commit()
            user_id = cur.fetchone()[0]
            return redirect('/customer_details/' + str(user_id))
        except psycopg2.Error as e:
            return f"Error creating account: {e}"
    else:
        return render_template('create_account.html')


@app.route('/customer_details/<int:user_id>', methods=['GET', 'POST'])
def customer_details(user_id):
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        phone_number = formatPhone(phone_number)

        cur.execute("INSERT INTO Customers (user_id, first_name, last_name, phone_number) VALUES (%s, %s, %s, %s)",
                    (user_id, first_name, last_name, phone_number))
        conn.commit()
        return redirect('/')
    else:
        return render_template('customer_details.html', user_id=user_id)


if __name__ == '__main__':
    app.run(debug=True)
