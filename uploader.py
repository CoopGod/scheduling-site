# PROGRAM FOR HARVARD'S CS50x
# TAKES ON CSV FILE AND UPLOADS IT TO SQL (what this file does)
# SQL IS THEN TAKEN TO A WEBSERVER AND IS AVAILABLE FOR EMPLOYEE'S TO MODIFY AND VIEW

from cs50 import SQL
import csv
import sys
from datetime import date, timedelta


def main():
    # Ensure proper CMD Line Arg
    if len(sys.argv) > 3:
        print("Error!")
        return 1

    # Upload CSV files and set DB
    schedule = sys.argv[1]
    open("schedule.db", "w").close()
    db = SQL(f"sqlite:///schedule.db")

    # Create Table
    db.execute("CREATE TABLE online (ID int, staff text, PRIMARY KEY (ID))")
    # Gather starting and finishing date
    # get inputs later-----------------------------------------
    startDate = date(2020, 12, 14)
    endDate = date(2021, 1, 17)
    delta = timedelta(days=1)

    # Open csv file and update SQL
    with open(schedule, "r") as schedule:

        reader = csv.DictReader(schedule)

        # Update Headers
        while startDate <= endDate:
            currentDate = startDate.strftime("%d-%b")
            db.execute("ALTER TABLE online ADD ? text", currentDate)
            startDate += delta

        rowCount = 1
        # Update values for
        for row in reader:
            # Insert staff member into row
            staff = row["Staff"]
            print(f"Staff Member: {staff}")
            db.execute("INSERT INTO online (staff, ID) VALUES (?, ?)", staff, rowCount)

            # Interate through dates to update rows for each staff member
            startDate = date(2020, 12, 14)
            while startDate <= endDate:
                currentDate = startDate.strftime("%d-%b")
                shift = row[currentDate]
                startDate += delta
                if shift != "NULL":
                    db.execute("UPDATE online SET ? = ? WHERE staff = ?", currentDate, shift, staff)
            rowCount += 1


if __name__ == "__main__":
    main()
