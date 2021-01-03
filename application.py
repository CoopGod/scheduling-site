# Import packages
import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, Markup
from flask_session import Session
from datetime import date, timedelta, datetime
# Load helper functions
from helper import *

# Configure application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'GM_CAL'

# Load database
db = SQL("sqlite:///schedule.db")


# Login Page (add hash, if user login, etc)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user = request.form.get('user')
        password = request.form.get('pass')
        data = db.execute("SELECT * FROM USERS WHERE staff = ?", user)
        if len(data) < 1:
            session['error'] = "User does not exist"
            return redirect('/error')
        elif data[0]['password'] == password:
            db.execute('UPDATE USERS SET iDelta = 0 WHERE staff = ?', user)
            session["user_id"] = data[0]['ID']
            return redirect("/calendar")
        else:
            session['error'] = "Password Incorrect"
            return redirect('/error')

    else:
        return render_template("index.html")


# Calendar Display
@login_required
@app.route("/calendar", methods=["GET", "POST"])
def calendar():
    userid = session["user_id"]
    if request.method == "POST":

        # Gather form data
        if request.form.get("traverseCalendarF"):
            # Grab update iDelta (calendar iteration)
            userData = db.execute('SELECT * FROM USERS WHERE ID = ?', userid) # need userid variable
            iterationRaw = userData[0]['iDelta']
            # Update based on choice
            iteration = int(iterationRaw) + 1
            db.execute('UPDATE USERS SET iDelta = ? WHERE ID = ?', iteration, userid)
            # Load data and redirect back to page
            data = loadCalendar(iteration)
            return redirect('/calendar')

        elif request.form.get("traverseCalendarB"):
            # Grab update iDelta (calendar iteration)
            userData = db.execute('SELECT * FROM USERS WHERE ID = ?', userid) # need userid variable
            iterationRaw = userData[0]['iDelta']
            # Update based on choice
            iteration = int(iterationRaw) - 1
            db.execute('UPDATE USERS SET iDelta = ? WHERE ID = ?', iteration, userid)
            # Load data and display template (clean up into one section)
            data = loadCalendar(iteration)
            return redirect('/calendar')

        elif request.form.get("addDate"):
            return redirect("/Add")

        elif request.form.get("removeData"):
            return redirect("/Delete")

    else:
        userData = db.execute('SELECT * FROM USERS WHERE ID = ?', userid) # need userid variable
        iterationRaw = userData[0]['iDelta']
        iteration = int(iterationRaw)
        data = loadCalendar(iteration)
        try:
            tableInfoHead, tableInfoBody = data
        except TypeError:
            session['error'] = "Movement past written schedule"
            return redirect("/error")
        return render_template("calendar.html", tableInfoHead=tableInfoHead, tableInfoBody=tableInfoBody)

# Add shift to SQL
@login_required
@app.route("/Add", methods=["GET", "POST"])
def addShift():
    if request.method == "POST":
        if request.form.get("submit"):
            # Gather input Data
            inputDate = request.form.get("date")
            inputStaff = request.form.get("staff")
            inputTime = request.form.get("time")

            # Import data from SQL
            staffMembers = db.execute("SELECT staff FROM online")
            staffMemberCountDic = db.execute("SELECT COUNT(staff) FROM online")
            staffMemberCount = staffMemberCountDic[0]["COUNT(staff)"]

            # Find Employee
            rowCount = 0
            while rowCount < staffMemberCount:
                if inputStaff in staffMembers[rowCount]["staff"]:
                    print(f"found: {inputStaff} at {rowCount + 1}")
                    break
                else:
                    rowCount += 1

            data = db.execute("SELECT * FROM online WHERE id = ?", rowCount + 1)

            # Check if employee exsists
            try:
                print(data[0][inputDate])
            except IndexError:
                session['error'] = "Employee Does not exsist"
                return redirect('/error')
            except KeyError:
                session['error'] = "Date Entered Wrong"
                return redirect('/error')

            # Update time into date
            db.execute("UPDATE online SET ? = ? WHERE id = ?", inputDate, inputTime, rowCount + 1)
            return redirect("/calendar")
    else:
        return render_template("addShift.html")

# Delete shift from SQL
@login_required
@app.route("/Delete", methods=["GET", "POST"])
def delShift():
    if request.method == "POST":
        if request.form.get("submit"):
            # Gather input info
            inputDate = request.form.get("date")
            inputStaff = request.form.get("staff")

            # Find employee count
            staffMembers = db.execute("SELECT staff FROM online")
            staffMemberCountDic = db.execute("SELECT COUNT(staff) FROM online")
            staffMemberCount = staffMemberCountDic[0]["COUNT(staff)"]

            # Find Employee
            rowCount = 0
            while rowCount < staffMemberCount:
                if inputStaff in staffMembers[rowCount]["staff"]:
                    print(f"found: {inputStaff} at {rowCount + 1}")
                    break
                else:
                    rowCount += 1

            data = db.execute("SELECT * FROM online WHERE id = ?", rowCount + 1)

            # Check if employee exsists
            try:
                print(data[0][inputDate])
            except IndexError:
                session['error'] = "Employee Does not exsist"
                return redirect('/error')

            # Update time into date
            db.execute("UPDATE online SET ? = ' ' WHERE id = ?", inputDate, rowCount + 1)
            return redirect("/calendar")

    else:
        return render_template("delShift.html")

@app.route("/error", methods=["GET"])
def error():
    error = session['error']
    return render_template('not_found.html', error=error)