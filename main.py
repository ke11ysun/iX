
# env local python3
# cmd "python3 main.py"

from flask import Flask, render_template, redirect, request, session, url_for
from util import recommend, augment_preference, filter_shows, select_seats
from util import get_user, get_movie

import sqlite3
from sqlite3 import Error

app = Flask(__name__)

def sql_connection():
	try:
		conn = sqlite3.connect('iX.db')
		return conn
	except Error:
		print(Error)

@app.route("/")
def index():
    title = "iX"
    session['conn'] = sql_connection()
    return render_template("index.html", title=title)

@app.route("/explore", methods=['POST', 'GET'])
def explore():
    # if 'recommended_mids' in session:
    #     mids = session['recommended_mids']
    #     print('has mids')
    # else:
    #     print('no mids')
    #     return render_template('explore.html', error="no mids")
    movies = []
    print('before for')
    mids = ['m001', 'm002', 'm003']
    for mid in mids:
        movie = {}
        entity = get_movie(mid)
        movie['mid'] = mid
        movie['name'] = entity['name']
        movie['genre'] = entity['genre']
        # etc
        print('=======')
        print(len(movies))
        movies.append(movie)
    return render_template("explore.html", len=len(movies), movies=movies)

@app.route("/form/<mname>", methods=['POST', 'GET'])
def form(mname):
    session['mname'] = mname
    return render_template("form.html", mname=mname)

@app.route("/inprogress", methods=['POST', 'GET'])
def inprogress():
    return render_template("inprogress.html")

@app.route("/purchased", methods=['POST', 'GET'])
def purchased():
    return render_template("purchased.html")

@app.route("/tickets", methods=['POST', 'GET'])
def tickets():
    preference = {}
    preference['num_tickets'] = int(request.form['num']) # cast to int
    preference['time'] = request.form['time']
    preference['date'] = request.form['date']
    preference['zip'] = request.form['zip_code']
    preference['self_input'] = request.form['self_input']

    # # filtering with rank, didn't test 0421
    # showings = filter_shows(session['mname'], preference, session['conn'])
    # return render_template("tickets.html", showings=showings)

    return render_template("tickets.html")



if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)