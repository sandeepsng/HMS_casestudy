from flask import Flask, render_template, request, url_for, redirect
import sqlite3
import datetime
import os

app = Flask(__name__)

conn = sqlite3.connect('hospital.db')
cur = conn.cursor()

## the following function is used to create the database
## and tables inside it.
## tables created: 
##               -- patients 
def createTable():	
	cur.execute('''CREATE TABLE IF NOT EXISTS patients (
		ws_ssn INTEGER UNIQUE,
		ws_pat_id INTEGER PRIMARY KEY AUTOINCREMENT,
		ws_pat_name TEXT NOT NULL,
		ws_adrs TEXT NOT NULL,
		ws_age INTEGER NOT NULL,
		ws_doj TEXT NOT NULL,
		ws_rtype TEXT,
		ws_status INTEGER DEFAULT 1
	) ''')
	conn.commit()

## return the current date in string type
## required format in case-study YYYY-MM-DD
def getCurrentDate():
	p = datetime.datetime.now()
	current_date = p.strftime("%Y-%m-%d")
	print(f"date_today: {current_date}")
	return current_date

## Inserting values and data into the tables
## inserting just for reference
## NOTE: Call this function only once at the time of running the app for the first time.
def insertIntoTable():
	date_today = getCurrentDate()	
	
	p_records = [
		(987412365,100000000,'natsu', 'f-street-01, fiore', 19,date_today,'General',1),
		(987412354,100000001,'gray', 'f-street-16, fiore', 19,date_today,'General',1)	
	]
	cur.executemany("INSERT INTO patients VALUES (?,?,?,?,?,?,?,?)" , p_records)
	print(f"INSERTED {cur.rowcount} rows")
	conn.commit()

## ========================================================================
## =========== FLASK ROUTES and LOGIC BELOW ===============================
## ========================================================================

@app.route('/')
@app.route('/index')
def indexPage():
	return render_template("index.html",pageTitle="Welcome to XYZ Hospital")

## view details of all the patients present in the "patients" table
@app.route('/patients')
def viewPatientDetails():
	patient_details = []
	conn2 = sqlite3.connect("hospital.db")
	c = conn2.cursor()
	c.execute("SELECT * from patients")
	for i in c.fetchall():
		patient_details.append(i)
	c.close()
	conn2.close()
	return render_template("patients.html",patient_details=patient_details,pageTitle="patients details")


## if GET request -> returns to the add-new-patient form/html page
## if POST request -> user has filled the "add new patient form" -> INSERT the patient details in the "patients" TABLE -> redirect to view all patients details
@app.route('/addnewpatient',methods=['GET','POST'])
def addNewPatient():
	if request.method == 'POST':
		conn = sqlite3.connect("hospital.db")
		c = conn.cursor()
		c.execute("INSERT INTO patients (ws_ssn, ws_pat_name, ws_adrs, ws_age, ws_doj, ws_rtype, ws_status) VALUES (?,?,?,?,?,?,?);", (request.form['p_ssn'],request.form['p_name'],request.form['p_addr'],request.form['p_age'],getCurrentDate(),request.form['p_rtype'],1))
		conn.commit()
		c.close()
		conn.close()
		return redirect(url_for('viewPatientDetails'))	
	return render_template("addnewpatients.html",pageTitle="add new patient")

if __name__ == '__main__':
	createTable()
	#insertIntoTable()
	conn.close()
	app.run(debug=True)