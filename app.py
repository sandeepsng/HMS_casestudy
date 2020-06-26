from flask import Flask, render_template, request, url_for, redirect
import sqlite3
import datetime
import os

app = Flask(__name__)

conn = sqlite3.connect('hospital.db')
cur = conn.cursor()

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

def getCurrentDate():
	p = datetime.datetime.now()
	current_date = p.strftime("%Y-%m-%d")
	print(f"date_today: {current_date}")
	return current_date


def insertIntoTable():
	date_today = getCurrentDate()	
	
	p_records = [
		(987412365,100000000,'natsu', 'f-street-01, fiore', 19,date_today,'General',1),
		(987412354,100000001,'gray', 'f-street-16, fiore', 19,date_today,'General',1)	
	]
	cur.executemany("INSERT INTO patients VALUES (?,?,?,?,?,?,?,?)" , p_records)
	print(f"INSERTED {cur.rowcount} rows")
	conn.commit()


@app.route('/')
def indexPage():
	return "hello"

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