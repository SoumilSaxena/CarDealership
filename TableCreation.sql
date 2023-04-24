CREATE TABLE Users(
	User_ID serial PRIMARY KEY,
	Username varchar(20) NOT NULL,
	Password varchar(192) NOT NULL,
	Level int NOT NULL
);
CREATE TABLE Locations(
	Location_ID serial PRIMARY KEY,
	Address varchar(255) UNIQUE NOT NULL,
	City varchar(255) NOT NULL
);
-- Is_Sold is redundant data given the existence of a sales table; a bool attribute here is easier to query 
CREATE TABLE Stock(
	VIN char(17) PRIMARY KEY,
	Make varchar(255),
	Color varchar(255),
	Model varchar(255),
	Year int,
	Starting_Price money,
	Is_Sold boolean
);
CREATE TABLE Roles(
	Role_ID serial PRIMARY KEY,
	Description varchar(255)
);
CREATE TABLE Employees(
	Employee_ID serial PRIMARY KEY,
	User_ID serial REFERENCES Users,
	Birthdate date,
	Salary money,
	First_Name varchar(255),
	Last_Name varchar(255),
	Address varchar(255),
	Role_ID int REFERENCES Roles ON DELETE
	SET NULL
);
CREATE TABLE Service_History(
	service_id serial PRIMARY KEY,
	VIN char(17) REFERENCES Stock ON DELETE CASCADE,
	custid int REFERENCES Users(User_ID) ON DELETE
	SET NULL,
		Mechanic int REFERENCES Employees(Employee_ID) ON DELETE
	SET NULL,
		service_date_requested date,
		service_date_completed date,
		service_type varchar(50),
		service_request_description varchar(255),
		service_description varchar(255),
		service_cost money,
		is_serviced boolean
);
CREATE TABLE Customers(
	Customer_ID serial PRIMARY KEY,
	User_ID serial REFERENCES Users,
	First_Name varchar(255),
	Last_Name varchar(255),
	Email_Address varchar(255),
	Phone_Number char(12)
);
CREATE TABLE Sales(
	VIN char(17) PRIMARY KEY REFERENCES Stock,
	Customer_ID serial REFERENCES CUSTOMERS,
	Selling_Price money,
	Dealer int REFERENCES Employees,
	Location int REFERENCES Locations
);
INSERT INTO Roles(Role_ID, Description)
VALUES(0, 'Admin'),
	(1, 'Dealer'),
	(2, 'Engineer'),
	(3, 'Customer'),
	(4, 'Mechanic');
INSERT INTO Locations (Address, City)
VALUES ('USF', 'Tampa');
INSERT INTO Locations (Address, City)
VALUES ('MIT', 'Boston');
INSERT INTO Locations (Address, City)
VALUES ('Beverly Hills', 'Los Angeles');
--Trigger to set is_sold value to true when addedeto stock, postgre requires function, cannot set trigger directly
CREATE OR REPLACE FUNCTION update_stock() RETURNS TRIGGER AS $$ BEGIN
UPDATE stock
SET is_sold = TRUE
WHERE vin = NEW.vin;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER sales_insert_trigger
AFTER
INSERT ON sales FOR EACH ROW EXECUTE FUNCTION update_stock();