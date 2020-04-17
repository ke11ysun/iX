
# env local python3
# cmd "python3 main.py"

from flask import Flask, render_template, redirect, request, session, url_for
from util import recommend, augment_preference, filter_shows, select_seats
from util import get_user, get_movie

app = Flask(__name__)

@app.route("/")
def index():
    title = "iX"
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
    return render_template("form.html", mname=mname)

@app.route("/inprogress", methods=['POST', 'GET'])
def inprogress():
    return render_template("inprogress.html")

@app.route("/purchased", methods=['POST', 'GET'])
def purchased():
    return render_template("purchased.html")

@app.route("/tickets", methods=['POST', 'GET'])
def tickets():
    num = request.form['num']
    time = request.form['time']
    date = request.form['date']
    zip_code = request.form['zip_code']
    # print(num)
    # print(time)
    # print(zip_code)
    return render_template("tickets.html")

@app.route("/login", methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        # save user id, name etc to session 
        logged_in = True
    if logged_in:
        return redirect('/movies')
    else:
        return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    return redirect('/')

@app.route("/movies", methods=['POST', 'GET'])
def movies():
    # need a "history" button, to viewing history and enable rating
    if request.method == 'POST':
        # user chooses movie
        # save movie id to session
        return redirect('/preferences')
    else:
        # retrieve movie list
        # if logged in, pass to recommender
        return render_template('/movies')

# @app.route("/explore", methods=['POST', 'GET'])
# def explore():
#     '''
#     GET: in: mids, display: movie list
#     POST: in: chosen mid from form, out/carry: chosen mid
#     '''
#     # TODO: Need a "history" button, to viewing history and enable rating
#
#     if request.method == 'POST':
#         # user chooses movie
#         chosen_mid = request.form.get("submit_button")
#         # save movie id to session
#         session['chosen_mid'] = chosen_mid
#         print("====== chosen mid in session ======", session['chosen_mid'])
#         return redirect('/preferences')
#     else:
#         # if 'mids' in request.args:
#         #     mids = request.args['mids']
#         if 'recommended_mids' in session:
#             mids = session['recommended_mids']
#         else:
#             return render_template('explore.html', error="no mids")
#         # retrieve movie list
#         movies = []
#         for mid in mids:
#             movie = {}
#             entity = get_movie(mid)
#             movie['mid'] = mid
#             movie['name'] = entity['name']
#             movie['genre'] = entity['genre']
#             # etc
#             movies.append(movie)
#         return render_template('explore.html', len=len(movies), movies=movies)

@app.route("/preferences", methods=['POST', 'GET'])
def preferences():
    if request.method == 'POST':
        # user submits preferences (select + self-input) 
        # run seat selection algo
        # generate share link
        return redirect('/showings')
    else:
        # return empty form
        # if logged in and have prev preference in db, pre fill form
        return render_template('/preferences')

@app.route("/showings", methods=['POST', 'GET'])
def showings():
    if request.method == 'POST':
        # user submits preferences form (select + self-input) 
        # save showing info in db, for further rating 
        return redirect('/payment')
    else:
        # return empty form
        # if logged in and have prev preference in db, pre fill form
        return render_template('/showings')

# do we need eg. another thread to listen and merge preferences??

@app.route("/payment", methods=['POST', 'GET'])
def payment():
    if request.method == 'POST':
        # user submits payment form (select + self-input) 
        # just save the info to db for now
        return redirect('/success')
    else:
        # return empty form
        # if logged in and have prev payment info in db, pre fill form
        return render_template('/payment')

@app.route("/success", methods=['POST', 'GET'])
def success():
    # display success 
    # wait
    return redirect('/movies')

@app.route("/history", methods=['POST', 'GET'])
def history():
    # retrieve viewing history, enable rating 
    return render_template('/history')

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)