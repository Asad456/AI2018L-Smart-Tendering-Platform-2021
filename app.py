from flask import Flask, render_template
import sqlite3 as sql
app = Flask(__name__)


@app.route('/')
def hello_world():
    print("hello world")
    con = sql.connect("tenders.db")
    con.row_factory = sql.Row
    
    cur = con.cursor()
    cur.execute("SELECT * FROM USER_DATA")
    
    rows = cur.fetchall(); 
    return render_template("index.html",rows=rows)


if __name__=="__main__":
    app.run(debug=True)