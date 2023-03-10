import psycopg2
import re
conn = psycopg2.connect("dbname=postgres user=postgres password=passwordhere")
cur = conn.cursor()


def addCar(vin, make, color, model, year, starting_price, is_sold):
    cur.execute("""
        INSERT INTO stock (vin, make, color, model, year, starting_price, is_sold)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """,
                (vin, make, color, model, year, starting_price, is_sold))


def addCustomer(customer_id, user_id, first_name, last_name, phone_number):
    cur.execute("""
        INSERT INTO customers(customer_id, user_id, first_name, lastName, phone_number)
        VALUES (%s, %s, %s, %s, %s);
        """,
                (customer_id, user_id, first_name, last_name, phone_number))


def addEmployee(employee_id, user_id, birthdate, salary, first_name, last_name, address, role_id):
    cur.execute("""
        INSERT INTO employees(employee_id, user_id, birthdate, salary, first_name, last_name, address, role_id)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s);
        """,
                (employee_id, user_id, birthdate, salary, first_name, last_name, address, role_id, sell_date))


def recordSale(vin, customer_id, selling_price, dealer, location, sell_date):
    cur.execute("""
        INSERT INTO sales(vin, customer_id, selling_price, dealer, location, sell_date)
        VALUES (%s, %s, %s, %s, %s, %s);
        """,
                (vin, customer_id, selling_price, dealer, location, sell_date))


def validateLogin(username, password):
    cur.execute("""
        SELECT user_id, level FROM users WHERE username = %s AND password = %s);
        """,
                (username, password))
    # assuming that no user has the same username and password
    cur.fetchdone()


def getUser(username, password):
    cur.execute("SELECT user_id, first_name, role_id FROM Vw_User_Info WHERE username = %s AND password = %s;",
                (username, password))
    # assuming that no user has the same username and password
    return cur.fetchone()


def verifyUserAvailable(s):
    cur.execute("SELECT user_id FROM Users WHERE username = %s;", (s,))
    return cur.fetchone() == None


def insertUser(username, password, fname, lname, phone):
    cur.execute("INSERT INTO Users(username, password) VALUES (%s, %s) RETURNING user_id;",
                (username, password))
    newUserId = cur.fetchone()[0]
    cur.execute("INSERT INTO Customers(user_id, first_name, last_name, phone_number) VALUES (%s, %s, %s, %s);",
                (newUserId, fname, lname, phone))
    conn.commit()


def formatPhone(num):
    num = re.sub("[ ()-]", '', num)

    if (len(num) == 10 and num.isnumeric()):
        return num[:3] + "-" + num[3:6] + "-" + num[6:]
    else:
        print(str(len(num)) + ", " + str(num.isnumeric()))
        return 0


def main():
    # login page should look at users table, check level, then direct to admin/customer/employee portal
    print("Welcome to the LRST Car Dealership Information System. To continue, you will need an account.")
    print("[1] Login to existing account")
    print("[2] Create new account")
    print()
    userChoice = input("Please enter your decision: ")

    if (userChoice == '1'):
        while True:
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            userVerificationResult = getUser(username, password)

            if userVerificationResult != None:
                break
            else:
                print(
                    "No such user with the given username and password. Please try again.")

        # if userVerificationResult[2] == 0:
        #    printAdminMenu()
        # elif userVerificationResult[2] == 1:
        #    printDealerMenu()
        # elif userVerificationResult[2] == 2:
        #    printMechanicMenu()
        # elif userVerificationResult[2] == 3:
        #    printCustomerMenu()

    elif (userChoice == '2'):
        print("If you are an employee, please contact your supervisor or system administrator to activate your account.")
        print()
        while True:
            username = input("Enter a username with 20 characters or less: ")
            if 0 < len(username) <= 20:
                if verifyUserAvailable(username):
                    break
                else:
                    print("Username already taken. Please try again.")
            else:
                print("Invalid username. Please try again.")
        while True:
            password = input("Enter a password with 20 characters or less: ")
            if 0 < len(password) <= 20:
                break
            else:
                print("Invalid password. Please try again.")
        fname = input("Enter your first name: ")
        lname = input("Enter your last name: ")
        while True:
            phone = input("Enter your phone number: ")
            formattedPhone = formatPhone(phone)
            if formattedPhone != 0:
                break
            else:
                print("Invalid format. Please try again.")
        insertUser(username, password, fname, lname, formattedPhone)

        # login somehow and then continue to menus


main()
