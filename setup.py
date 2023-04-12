from flask import Flask, render_template, request, redirect
import psycopg2
import hashlib
import binascii
import os
import re
app = Flask(__name__)
conn = psycopg2.connect("dbname=dbdesign user=postgres password=Soumil008")
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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/view_cars')
def view_cars():
    return "View Cars"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # query user password hash
        try:
            cur.execute(
                "SELECT password FROM users WHERE username = %s", (username,))
        except psycopg2.Error as e:
            print(f"\nError selecting password in: {e}")
            return "Error"
        stored_database_password = cur.fetchone()
        if stored_database_password is None:
            print("User not found")
            return "User not found"
        stored_database_password = stored_database_password[0]
        if not verify_password(stored_database_password, password):
            print("Incorrect username or password")
            return "Incorrect username or password"
        print("Password Verified")
        try:
            cur.execute(
                "SELECT user_id FROM users WHERE username = %s AND password = %s", (username, stored_database_password))
            user_id = cur.fetchone()
            if user_id:
                print("Login successful.")
                return "Login successful"
            else:
                print("Incorrect username or password.")
                return "Incorrect username or password"
        except psycopg2.Error as e:
            print(f"\nError logging in: {e}")
            return "Error"
    return render_template('login.html')


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
