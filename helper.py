# Import packages
import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, Markup
from datetime import date, timedelta, datetime
from functools import wraps

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///schedule.db")


def loadCalendar(inputForDelta):
    try:
        # Declare date and end date for display of SQL
        delta = timedelta(days=1)
        deltaInteration = (delta * 7) * inputForDelta

        # Gather Current date
        todayDate = datetime.now()
        print(todayDate)
        todayDateRaw = str(todayDate).split(' ')
        outputDate = str(todayDateRaw[0]).split("-")

        startDate = date(int(outputDate[0]), int(outputDate[1]), int(outputDate[2])) + deltaInteration
        print(startDate)
        endDate = startDate + (delta * 6)

        # Table variables
        tableInfoHead = Markup("<th>Staff</th>")
        tableInfoBody = Markup("")

        # Insert Headers
        while startDate <= endDate:
            currentDate = startDate.strftime("%d-%b")
            startDate += delta
            tableInfoHead += Markup(f"<th>{currentDate}</th>")

        # Insert Info According to Date (7 days at a time)
        startDate = date(int(outputDate[0]), int(outputDate[1]), int(outputDate[2])) + deltaInteration
        displayData = db.execute("SELECT * FROM online WHERE ? = ?", currentDate, currentDate)

        tableInfoBody = Markup("")
        i = 0
        while i < len(displayData):
            staff = displayData[i]["staff"]
            tableInfoBody += Markup(f"<tr><td>{staff}</td>")

            startDate = date(int(outputDate[0]), int(outputDate[1]), int(outputDate[2])) + deltaInteration
            while startDate <= endDate:
                currentDate = startDate.strftime("%d-%b")
                dateInteration = displayData[i][currentDate]
                tableInfoBody += Markup(f"<td>{dateInteration}</td>")
                startDate += delta
            tableInfoBody += Markup("</tr>")
            i += 1

        # return Values
        return tableInfoHead, tableInfoBody
    except KeyError:
        session['error'] = "Movement past written schedule"
        return redirect("/error")


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged in' in session:
            return f(*args, **kwargs)
        else:
            return redirect("/")

    return wrap
