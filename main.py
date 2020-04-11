
# env local python3
# cmd "python3 main.py"

from flask import Flask, render_template, redirect, request, session, url_for

app = Flask(__name__)

@app.route("/")
def index():
    # index page = title pic + "let's get started"
    return render_template("index.html")

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