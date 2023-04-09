import re
import psycopg2
import hashlib #used for password hash
import binascii #used for password hash
import os #used for password hash random character
# Global variables to store the logged-in user ID and their access level
logged_in_user = None
logged_in_user_level = None


# def create_tables():
#     commands = [
#         """
#         CREATE TABLE Users(
#             User_ID serial PRIMARY KEY,
#             Username varchar(20) NOT NULL,
#             Password varchar(20) NOT NULL,
#             Level int NOT NULL
#         )
#         """,
#         """
#         CREATE TABLE Locations(
#             Location_ID serial PRIMARY KEY,
#             Address varchar(255) UNIQUE NOT NULL
#         )
#         """,
#         """
#         CREATE TABLE Stock(
#             VIN char(17) PRIMARY KEY,
#             Make varchar(255),
#             Color varchar(255),
#             Model varchar(255),
#             Year int,
#             Starting_Price money,
#             Is_Sold boolean
#         )
#         """,
#         """
#         CREATE TABLE Roles(
#             Role_ID serial PRIMARY KEY,
#             Description varchar(255)
#         )
#         """,
#         """
#         CREATE TABLE Employees(
#             Employee_ID serial PRIMARY KEY,
#             User_ID int REFERENCES Users,
#             Birthdate date,
#             Salary money,
#             First_Name varchar(255),
#             Last_Name varchar(255),
#             Address varchar(255),
#             Role_ID int REFERENCES Roles ON DELETE SET NULL
#         )
#         """,
#         """
#         CREATE TABLE Service_History(
#             VIN char(17) REFERENCES Stock ON DELETE CASCADE,
#             Mechanic int REFERENCES Employees ON DELETE SET NULL
#         )
#         """,
#         """
#         CREATE TABLE Customers(
#             Customer_ID serial PRIMARY KEY,
#             User_ID int REFERENCES Users,
#             First_Name varchar(255),
#             Last_Name varchar(255),
#             Phone_Number char(12)
#         )
#         """,
#         """
#         CREATE TABLE Sales(
#             VIN char(17) PRIMARY KEY REFERENCES Stock,
#             Customer_ID int REFERENCES CUSTOMERS,
#             Selling_Price money,
#             Dealer int REFERENCES Employees,
#             Location int REFERENCES Locations
#         )
#         """,
#         """
#         INSERT INTO Roles(Role_ID,Description)
#         VALUES(0,'Admin'),(1,'Dealer'),(2,'Engineer')
#         """
#     ]
#     conn = None
#     try:
#         conn = psycopg2.connect(
#             "dbname=postgres user=postgres password=")
#         cur = conn.cursor()
#         for command in commands:
#             cur.execute(command)
#         cur.close()
#         conn.commit()
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#     finally:
#         if conn is not None:
#             conn.close()


# Establish a connection to the database
conn = psycopg2.connect("dbname=postgres user=postgres password=Soumil008")

# Create a cursor object to interact with the database
cur = conn.cursor()


def main():
    # create_tables()
    global logged_in_user
    global logged_in_user_level

    print("Welcome to the car dealership inventory management system!")
    while True:
        print("\nPlease choose an option:")
        print("1. Log in")
        print("2. Create an account")
        print("3. Exit")
        choice = input("- ")
        if choice == "1":
            logged_in_user = login()
            if logged_in_user:
                # Retrieve the user's access level from the database
                cur.execute(
                    "SELECT level FROM users WHERE user_id = %s", (logged_in_user,))
                logged_in_user_level = cur.fetchone()[0]
                menu()
        elif choice == "2":
            create_account()
        elif choice == "3":
            conn.close()
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


def create_account():
    print("\nPlease enter your information:")
    username = input("Username: ")
    password = input("Password: ")
    level = input("Access level (0 for admin, 1 for dealer, 2 for engineer): ")
    hash_password = hash_password(password) #Password gets hashed
    # Check if username or password already exists
    cur.execute(
        "SELECT user_id FROM Users WHERE username = %s OR password = %s", (username, password))
    existing_user = cur.fetchone()
    if existing_user:
        print("\nError creating account: Username or password already exists.")
        return

    try:
        cur.execute("INSERT INTO Users (username, password, level) VALUES (%s, %s, %s) RETURNING user_id", (username, hash_password, level))
        #cur.execute("INSERT INTO Users (username, password, level) VALUES (%s, %s, %s) RETURNING user_id",
        #            (username, password, level))
        user_id = cur.fetchone()[0]
        print(f"\nAccount created successfully. Your user ID is {user_id}.")

        # Insert customer details
        first_name = input("First Name: ")
        last_name = input("Last Name: ")
        phone_number = input("Phone Number: ")
        phone_number = formatPhone(phone_number)

        cur.execute("INSERT INTO Customers (user_id, first_name, last_name, phone_number) VALUES (%s, %s, %s, %s)",
                    (user_id, first_name, last_name, phone_number))
        conn.commit()

    except psycopg2.Error as e:
        print(f"\nError creating account: {e}")

def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    hash_password = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 200000)
    hash_password = binascii.hexlify(hash_password)
    return (salt+hash_password).decode('ascii')

def verify_password(stored_password, provided_password):
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    hash_password = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 200000)
    computed_stored_password = binascii.hexlify(hash_password).decode('ascii')
    return stored_password == computed_stored_password

def update_passwords_to_hash():
    #delete me after running once to update the passwords to be hashed
    cur.execute("SELECT User_Id, Password FROM Users")
    rows = cur.fetchall()
    #loop through each row and update the password
    for row in rows:
        user_id = row[0]
        password = row[1]
        #hash the password
        hashed_password = hash_password(password)
        #update the user's password in the database
        print("Now updating User: %s", user_id)
        cur.execute("UPDATE Users SET Password = %s WHERE User_ID = %s", (hashed_password,))
        conn.commit()
    print("Finished Updating Passwords")
    return

def formatPhone(num):
    num = re.sub("[ ()-]", '', num)

    if (len(num) == 10 and num.isnumeric()):
        return num[:3] + "-" + num[3:6] + "-" + num[6:]
    else:
        print(str(len(num)) + ", " + str(num.isnumeric()))
        return 0


def login():
    print("\nPlease enter your login information:")
    username = input("Username: ")
    password = input("Password: ")
    #query user password hash
    cur.execute("SELECT password FROM users WHERE username = %s", (username,))
    stored_database_password = cur.fetchone()
    if verify_password(stored_database_password, password):
        #Password verified
        print()
    else:
        #Incorrect Password
        print("Incorrect username or password")
        return None
    try:
        cur.execute(
            "SELECT user_id FROM users WHERE username = %s AND password = %s", (username, password))
        user_id = cur.fetchone()
        if user_id:
            print("Login successful.")
            return user_id[0]
        else:
            print("Incorrect username or password.")
            return None
    except psycopg2.Error as e:
        print(f"\nError logging in: {e}")
        return None


def menu():
    while True:
        print("\nPlease choose an option:")
        print("1. Add a car to inventory")
        print("2. Add a customer")
        print("3. Add an employee")
        print("4. Record a sale")
        print("5. Log out")
        choice = input("> ")
        if choice == "1":
            if logged_in_user_level == 0 or logged_in_user_level == 1:
                # ask for details
                add_car()
            else:
                print("You do not have permission to perform this action.")
        elif choice == "2":
            if logged_in_user_level == 0 or logged_in_user_level == 1:
                
                add_customer()
            else:
                print("You do not have permission to perform this action.")
        elif choice == "3":
            if logged_in_user_level == 0:
                # ask for details
                add_employee()
            else:
                print("You do not have permission to perform this action.")
        elif choice == "4":
            if logged_in_user_level == 0 or logged_in_user_level == 1:
                print("Enter the following information. If unknown, leave blank:")
                vin, customer_id, dealer, selling_price, location, sell_date = None
                vin = input("VIN of car sold: ")
                customer_id = input("Customer ID of person the car was sold to: ")
                dealer = input("ID of person who sold the car: ")
                selling_price = input("How much was the car sold for: ")
                location = input("Which location (number) did the sale take place: ")
                sell_date = input("When was the car sold: ")
                record_sale(vin, customer_id, selling_price, dealer, location, sell_date)
        


def add_car(vin, make, color, model, year, starting_price, is_sold):
    cur.execute("""
        INSERT INTO stock (vin, make, color, model, year, starting_price, is_sold)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """,
                (vin, make, color, model, year, starting_price, is_sold))
    conn.commit()


def add_customer(customer_id, user_id, first_name, last_name, phone_number):
    cur.execute("""
        INSERT INTO customers(customer_id, user_id, first_name, last_name, phone_number)
        VALUES (%s, %s, %s, %s, %s);
        """,
                (customer_id, user_id, first_name, last_name, phone_number))
    conn.commit()


def add_employee(employee_id, user_id, birthdate, salary, first_name, last_name, address, role_id):
    cur.execute("""
        INSERT INTO employees(employee_id, user_id, birthdate, salary, first_name, last_name, address, role_id)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s);
        """,
                (employee_id, user_id, birthdate, salary, first_name, last_name, address, role_id))
    conn.commit()


def record_sale(vin, customer_id, selling_price, dealer, location, sell_date):
    cur.execute("""
        INSERT INTO sales(vin, customer_id, selling_price, dealer, location, sell_date)
        VALUES (%s, %s, %s, %s, %s, %s);
        """,
                (vin, customer_id, selling_price, dealer, location, sell_date))
    conn.commit()


main()
