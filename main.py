import re
import psycopg2
import hashlib #used for password hash
import binascii #used for password hash
import os #used for password hash random character
# Global variables to store the logged-in user ID and their access level
logged_in_user = None
logged_in_user_level = None

def collapseComment():
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
#             Email_Address varchar(255),
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
    print()

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
                if(logged_in_user_level == 0):
                    menu_admin()
                elif(logged_in_user_level == 1):
                    menu_dealer()
                elif(logged_in_user_level == 2):
                    menu_enginner()
                elif(logged_in_user_level == 3):
                    menu_customer()

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
    level = input("Access level (0 for admin, 1 for dealer, 2 for engineer, 3 for customer): ")
    password = hash_password(password) #Password gets hashed
    # Check if username or password already exists
    cur.execute(
        "SELECT user_id FROM Users WHERE username = %s OR password = %s", (username, password))
    existing_user = cur.fetchone()
    if existing_user:
        print("\nError creating account: Username or password already exists.")
        return
    try:
        cur.execute("INSERT INTO Users (username, password, level) VALUES (%s, %s, %s) RETURNING user_id", (username, password, level))
        #cur.execute("INSERT INTO Users (username, password, level) VALUES (%s, %s, %s) RETURNING user_id",
        #            (username, password, level))
        user_id = cur.fetchone()[0]
        print(f"\nAccount created successfully. Your user ID is {user_id}.")
        conn.commit()
    except psycopg2.Error as e:
        print(f"\nError creating account: {e}")
    if level == 0 or level == 1 or level == 2:
        add_employee()
    elif level == 3:
        # Insert customer details
        add_customer()

def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    hash_password = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 200000)
    hash_password = binascii.hexlify(hash_password)
    return (salt + hash_password).decode('ascii')

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
    try:
        cur.execute("SELECT password FROM users WHERE username = %s", (username,))
    except psycopg2.Error as e:
        print(f"\nError selecting password in: {e}")
        return None
    stored_database_password = cur.fetchone()[0]
    print(stored_database_password)
    if not verify_password(stored_database_password, password):
        #Incorrect Password
        print("Incorrect username or password")
        return None
    #Password verified
    print("Password Verified")
    try:
        cur.execute(
            "SELECT user_id FROM users WHERE username = %s AND password = %s", (username, stored_database_password))
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

def menu_admin():
    print("\nPlease choose an option:")
    #add
    print("1. Add a car to inventory")
    print("2. Add a customer")
    print("3. Add an employee")
    print("4. Add a sale")
    #remove
    print("5. Remove a car from inventory")
    print("6. Remove a customer")
    print("7. Remove an employee")
    print("8. Remove a sale") #Should not be used
    #list
    print("9. List cars")
    print("10. List customers")
    print("11. List employees")
    print("12. List sales")

    print("9. Log out")
    choice = input("> ")
    if choice == "1":
        add_car()
    elif choice == "2":
        add_customer()
    elif choice == "3":
        add_employee()
    elif choice == "4":
        add_sale()
    elif choice == "5":
        remove_car() #uses vin number to remove
    elif choice == "6":
        remove_customer() #TODO
    elif choice == "7":
        remove_employee() #TODO
    elif choice == "8":
        remove_sale() #TODO
    elif choice == "9":
        list_cars()
    elif choice == "10":
        list_customer()
    return

def menu_dealer():
    print("\nPlease choose an option:")
    print("1. Add a car to inventory")
    print("2. Add a customer")
    print("3. Record a sale")

def menu_enginner():
    print("\nPlease choose an option:")
    #TODO

def menu_customer():
    print("\nPlease choose an option:")
    #TODO

def menu():
    while True:
        print("\nPlease choose an option:")
        print("1. Add a car to inventory") #dealer
        print("2. Add a customer") #dealer
        print("3. Add an employee") #admin
        print("4. Record a sale") #dealer
        print("5. Log out")
        choice = input("> ")
        if choice == "1":
            if logged_in_user_level == 0 or logged_in_user_level == 1:
                add_car() #asks for details then calls add_car(...) for insert into db
            else:
                print("You do not have permission to perform this action.")
        elif choice == "2":
            if logged_in_user_level == 0 or logged_in_user_level == 1:
                add_customer() #asks for detils then calls add_customer(...) for insert into db
            else:
                print("You do not have permission to perform this action.")
        elif choice == "3":
            if logged_in_user_level == 0:
                add_employee() #asks for details then calls add_employee(...) for insert into db
            else:
                print("You do not have permission to perform this action.")
        elif choice == "4":
            if logged_in_user_level == 0 or logged_in_user_level == 1:
                add_sale #asks for details then calls record_sale(...) for insert into db
        elif choice == "5":
            exit()

#Start Car
def list_cars():
    #Prints cars that have not been sold, maybe ORDER BY make
    try:
        cur.execute("SELECT * FROM stock WHERE is_sold = false")
        rows = cur.fetchall()
        print("Current car stock:")
        for row in rows:
            print(f"VIN: {row[0]}, Make: {row[1]}, Color: {row[2]}, Model: {row[3]}, Year: {row[4]}, Starting Price: {row[5]}, Is Sold: {row[6]}")
    except psycopg2.Error as e:
        print(f"\nError listing cars: {e}")

def list_cars_by_attribute():
    make, model, year = None
    make = input("Make of car: ")
    model = input("Model of car: ")
    year = input("Year of car: ")
    query = "SELECT * FROM stock WHERE 1=1"
    params = []
    if make:
        query += " AND make = %s"
        params.append(make)
    if model:
        query += " AND model = %s"
        params.append(model)
    if year:
        try:
            int(year)
        except ValueError:
            print("Year must be a valid integer.")
            return
        query += " AND year = %s"
        params.append(year)
    try:
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        for row in rows:
                print(f"VIN: {row[0]}, Make: {row[1]}, Color: {row[2]}, Model: {row[3]}, Year: {row[4]}, Starting Price: {row[5]}, Is Sold: {row[6]}")
    except psycopg2.Error as e:
        print(f"\nError listing cars: {e}")
    return

def search_car_by_vin():
    vin = input("Enter VIN: ")
    try:
        cur.execute("SELECT * FROM stock WHERE vin = %s", (vin,))
        row = cur.fetchone()
        if row:
            print(f"VIN: {row[0]}, Make: {row[1]}, Color: {row[2]}, Model: {row[3]}, Year: {row[4]}, Starting Price: {row[5]}, Is Sold: {row[6]}")
        else:
            print("No car found with that VIN.")
    except psycopg2.Error as e:
        print(f"\nError searching for car: {e}")

def get_car_input():
    print("Enter the following information for car. If unkown, leave blank:")
    vin, make, color, model, year, starting_price, is_sold = None
    vin = input("VIN of car: ")
    make = input("Make of car: ")
    color = input("Color of car: ")
    model = input("Model of car: ")
    year = input("Year of car: ")
    starting_price = input("Starting Price of car: ")
    is_sold = input("Has the car been sold (boolean): ")
    return vin, make, color, model, year, starting_price, is_sold

def remove_car():
    vin = input("VIN of car: ")
    try:
        cur.execute("""DELETE FROM stock WHERE vin = %s;""", (vin,))
        conn.commit()
        print("Car removed successfully")
    except psycopg2.Error as e:
        print(f"\nError removing car: {e}")
    return

def add_car():
    vin, make, color, model, year, starting_price, is_sold = get_car_input()
    add_car(vin, make, color, model, year, starting_price, is_sold)

def add_car(vin, make, color, model, year, starting_price, is_sold):
    try:
        cur.execute("""
            INSERT INTO stock (vin, make, color, model, year, starting_price, is_sold)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """,
                    (vin, make, color, model, year, starting_price, is_sold))
        conn.commit()
    except psycopg2.Error as e:
        print(f"\nError creating account: {e}")
#End Car


#Start Customer
def add_customer():
    print("Enter the following information about a new customer. If unkown, leave blank:")
    first_name, last_name, email_address, phone_number = None
    email_address = input("Enter customer email: ")
    first_name = input("Enter customer first name: ")
    last_name = input("Enter customer last name: ")
    phone_number = input("Enter customer phone number: ")
    add_customer(first_name, last_name, email_address, phone_number)

def add_customer(first_name, last_name, email_address, phone_number):
    try:
        cur.execute("""
            INSERT INTO customers(first_name, last_name, email_address, phone_number)
            VALUES (%s, %s, %s, %s, %s);
            """,
                    (first_name, last_name, email_address, phone_number))
        conn.commit()
    except psycopg2.Error as e:
        print(f"\nError creating account: {e}")

def list_customer():
    try:
        cur.execute("SELECT Customer_ID, First_Name, Last_Name, Email_Address, Phone_Number FROM customers")
        rows = cur.fetchall()
        if rows:
            print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Phone':<15}")
            print("-" * 70)
            for row in rows:
                print(f"{row[0]:<5} {row[1]} {row[2]:<20} {row[3]:<30} {row[4]:<15}")        
        else:
            print("No customers found.")
    except psycopg2.Error as e:
        print(f"\nError listing customers: {e}")


def remove_customer():

    return
#End Customer

#Start Employee
def add_employee():
    print("Enter the following information for adding a new employee. If unknown, leave blank:")
    birthdate, salary, first_name, last_name, address = None
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    address = input("Enter address: ")
    salary = input("Enter salary: ")
    birthdate = input("Enter birthday (date): ")
    role_id = input("Access level (1 for dealer, 2 for engineer): ")
    add_employee(birthdate, salary, first_name, last_name, address, role_id)
    

def add_employee(birthdate, salary, first_name, last_name, address, role_id):
    try:
        cur.execute("""
        INSERT INTO employees(birthdate, salary, first_name, last_name, address, role_id)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s);
        """,
                (birthdate, salary, first_name, last_name, address, role_id))
        conn.commit()
    except psycopg2.Error as e:
        print(f"\nError creating account: {e}")

def remove_employee():
    return
#End Employee

#Start Sale
def add_sale():
    print("Enter the following information. If unknown, leave blank:")
    vin, customer_id, dealer, selling_price, location, sell_date = None
    vin = input("VIN of car sold: ")
    customer_id = input("Customer ID of person the car was sold to: ")
    dealer = input("ID of person who sold the car: ")
    selling_price = input("How much was the car sold for: ")
    location = input("Which location (number) did the sale take place: ")
    sell_date = input("When was the car sold: ")
    record_sale(vin, customer_id, selling_price, dealer, location, sell_date)

def record_sale(vin, customer_id, selling_price, dealer, location, sell_date):
    try:
        cur.execute("""
            INSERT INTO sales(vin, customer_id, selling_price, dealer, location, sell_date)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
                    (vin, customer_id, selling_price, dealer, location, sell_date))
        conn.commit()
    except psycopg2.Error as e:
        print(f"\nError creating account: {e}")

def remove_sale():
    return
#End Sale

main()
