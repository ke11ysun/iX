
# env local python3
# cmd "python3 main.py"

from flask import Flask, render_template, redirect, request, session, url_for
from util import recommend, augment_preference, filter_shows, select_seats
from util import get_user, get_movies, safe_cast, update_purchase, get_purchase
from movie_recommender import recommend_movie

import sqlite3
from sqlite3 import Error

from pprint import pprint

app = Flask(__name__)
app.secret_key = 'asdjkhahuehasjkjsadljasudslhugaf'
conn = None

def sql_connection():
    try:
        conn = sqlite3.connect('iX.db', check_same_thread=False)
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        print('DB connected')
        return conn
    except Error:
        print(Error)

@app.route("/")
def index():
    title = "iX"
    return render_template("index.html", title=title)

@app.route("/explore", methods=['POST', 'GET'])
def explore():
    ## if logged in and user_id in session:
    # user_id = session['user_id'] 
    # now test with user_id = 0,1,...,20:
    user_id = 0
    recmmend_movies = recommend_movie(user_id=user_id,
                           recommend_range=None,
                           recommend_number=5)
    print('recommend movies:\n', recmmend_movies)
    
    # tuple of recommended movie ids, sorted descendingly by recommendation scores:
    # mids = tuple(recmmend_movies.movie_id)
    mids = (1,2,3)
    print('mids:\n', mids)
    
    # select movies of which ids are in mids:
    # movies = get_movies(conn, mids)
    movies = get_movies(conn)
    # print(movies)
    return render_template("explore.html", len=len(movies), movies=movies)

@app.route("/form/<mname>", methods=['POST', 'GET'])
def form(mname):
    session['mname'] = mname
    return render_template("form.html", mname=mname)

@app.route("/form/<mname>/<random>", methods=['POST', 'GET'])
def link_form(mname, random):
    return render_template("form.html", mname=mname)

@app.route("/inprogress", methods=['POST', 'GET'])
def inprogress():
    return render_template("inprogress.html")

@app.route("/purchased", methods=['POST', 'GET'])
def purchased():
    return render_template("purchased.html")

@app.route("/success", methods=['POST', 'GET'])
def success():
    return render_template("success.html")

@app.route("/tickets", methods=['POST', 'GET'])
def tickets():
    print("form", request.form)
    print("form", request.form.to_dict())
    preference = {}
    preference['num_tickets'] = safe_cast(request.form, 'num', 3, True) # cast to int
    preference['time'] = safe_cast(request.form, 'time', "13:00")
    print('preference time', preference['time'])
    preference['date'] = safe_cast(request.form, 'date', "2020-04-22")
    preference['zip'] = safe_cast(request.form, 'zip_code', "10003")
    preference['self_input'] = safe_cast(request.form, 'self_input', "")
    mname = safe_cast(session, 'mname', "Trolls World Tour")
    pprint(preference)
    update_purchase(conn, preference)

    showings = filter_shows(mname, preference, conn)
    # print("Recommended showings: ", showings)
    return render_template("tickets.html", len=len(showings), showings=showings, mname=mname)

@app.route("/tickets/<mname>", methods=['GET'])
def tickets_refresh(mname):
    preference = get_purchase(conn)[0]
    preference['time'] = preference['show_time']
    preference['date'] = preference['show_date']
    showings = filter_shows(mname, preference, conn)
    return render_template("tickets.html", len=len(showings), showings=showings, mname=mname)



if __name__ == "__main__":
    conn = sql_connection()
    app.run(host= '0.0.0.0', port="8080")
