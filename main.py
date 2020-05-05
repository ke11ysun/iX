from flask import Flask, render_template, redirect, request, session, url_for
from util import filter_shows, get_movies, safe_cast, update_purchase, get_purchase, get_mname
from movie_recommender import recommend_movie
import numpy as np
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

@app.route("/explore/", methods=['POST', 'GET'])
@app.route("/explore/<user_id>", methods=['POST', 'GET'])
def explore(user_id=0):
    ## if logged in and user_id in session:
    # user_id = session['user_id'] 
    # user_id = 0
    print("user id: ", user_id)
    recmmend_movies = recommend_movie(user_id=user_id,
                           recommend_range=None,
                           recommend_number=5)
    print('recommend movies:\n', recmmend_movies)
    
    # tuple of recommended movie ids, sorted descendingly by recommendation scores:
    # mids = tuple(recmmend_movies.movie_id)
    # kelly: from db the only workable mids are 1, 6, 8, 12, 14, 15, 21, 28, 33, 44, 54, 107, 352
    # mids = tuple(np.random.choice([0, 1, 14, 19, 16, 10, 29, 5, 36, 42, 62, 11, 106], size=6, replace=False))
    candidates = [0, 14, 19, 16, 10, 29, 5, 36, 42, 62, 11, 106]
    if user_id != 0:
        mids = tuple([1] + np.random.choice(candidates, size=5, replace=False).tolist())
    else:
        mids = tuple(candidates)
    print('recommend mids:\n', mids)
    
    # select movies of which ids are in mids:
    movies = get_movies(conn, mids)
    return render_template("explore.html", len=len(movies), movies=movies, user=user_id)

@app.route("/login", methods=['POST', 'GET'])
def login():
    return render_template("login.html")

@app.route("/form/<mid>", methods=['POST', 'GET'])
def form(mid):
    mname = get_mname(conn, mid)
    print("MID -> mname::")
    print(mname)
    session['mname'] = mname
    session['mid'] = mid
    return render_template("form.html", mid=mid, mname=mname)
# @app.route("/form/<mname>", methods=['POST', 'GET'])
# def form(mname):
#     session['mname'] = mname
#     return render_template("form.html", mname=mname)

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
    form = dict(request.form.lists())
    for k, v in form.items():
        content = [s for s in v if s != '']
        if len(content) > 0:
            form[k] = content[0]
        else:
            form[k] = ''
    print('form:\n', form)

    preference = {}
    preference['num_tickets'] = safe_cast(form, 'num', 3, True) # cast to int
    preference['time'] = safe_cast(form, 'time', "13:00")
    preference['date'] = safe_cast(form, 'date', "2020-04-22")
    preference['zip'] = safe_cast(form, 'zip_code', "10003")
    preference['self_input'] = safe_cast(form, 'self_input', "")
    mname = safe_cast(session, 'mname', "Trolls World Tour")
    pprint(preference)
    update_purchase(conn, preference)

    showings = filter_shows(mname, preference, conn)
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
