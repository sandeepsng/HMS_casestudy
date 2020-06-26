from flask import Flask, render_template, request
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


def insertIntoTable():
	p = datetime.datetime.now()
	date_today = p.strftime("%Y-%m-%d")
	print(f"date_today: {date_today}")
	
	
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
	


if __name__ == '__main__':
	createTable()
	#insertIntoTable()
	app.run(debug=True)