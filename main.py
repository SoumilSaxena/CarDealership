import re
import psycopg2
import hashlib #used for password hash
import binascii #used for password hash
import os #used for password hash random character
from setup import conn, cur
# Global variables to store the logged-in user ID and their access level
logged_in_user = None
logged_in_user_level = None



# Establish a connection to the database
#conn = psycopg2.connect("dbname=postgres user=postgres password=?????")

# Create a cursor object to interact with the database
conn = psycopg2.connect("dbname= user=postgres password=")
#enter name of database and your password
#cur = conn.cursor()


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
                    menu_engineer()
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
    conn = psycopg2.connect("dbname= user=postgres password=")
    #enter name of database and your password to pgadmin
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id FROM Users WHERE username = %s OR password = %s", (username, password))
    existing_user = cur.fetchone()
    if existing_user:
        print("\nError creating account: Username or password already exists.")
        return
    try:
        cur.execute("INSERT INTO Users (username, password, level) VALUES (%s, %s, %s) RETURNING user_id", (username, password, level))
        user_id = cur.fetchone()[0]
        print(f"\nAccount created successfully. Your user ID is {user_id}.")
        print(level)
        conn.commit()
        if level == '0' or level == '1' or level == '2':
            first_name = input("Enter first name: ")
            last_name = input("Enter last name: ")
            address = input("Enter address: ")
            salary = input("Enter salary: ")
            birthdate = input("Enter birthday (date): ")
            level = int(level)
            cur.execute("INSERT INTO employees(user_id, first_name, last_name, Birthdate, salary, address, role_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (user_id, first_name, last_name, birthdate, salary, address, level))
            conn.commit()
            print("\nAdded to employees.")
    except psycopg2.Error as e:
        print(f"\nError creating account: {e}")
    if level == 0 or level == 1 or level == 2:
        pass


def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    hash_password = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 200000)
    hash_password = binascii.hexlify(hash_password)
    return (salt + hash_password).decode('ascii')


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


main()