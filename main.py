
# env local python3
# cmd "python3 main.py"

from flask import Flask, render_template, redirect, request, session, url_for
from util import recommend, augment_preference, filter_shows, select_seats 
from util import get_user, get_movie

app = Flask(__name__)
app.secret_key = 'asdjkhahuehasjkjsadljasudslhugaf'

@app.route("/")
def index():
    title = "iX"
    return render_template("index.html", title=title)


@app.route("/login", methods=['POST', 'GET'])
def login():
    '''
    in: login form, out: recommended mids, carry: uid
    '''
    error = None
    loaded = False
    if 'uid' in session:
        loaded = True

    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        if len(username) != 0:
            loaded = True
            user_entity = get_user(username, password)
            if not user_entity:
                error = "No username found"
                loaded = False
            elif user_entity["password"] != password:
                error = "Please use make sure your password is correct!"
                loaded = False
    if loaded:
        # if logged in, pass to recommender
        session['user'] = user_entity
        mids = recommend(user_entity['uid'])
        session['recommended_mids'] = mids
        # return redirect(url_for('.explore', mids=mids))  
        return redirect('/explore')  
    else:
        return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    del session['user']
    del session['chosen_mid']
    del session['num_tickets']
    del session['chosen_dis']
    del session['recommended_mids']
    del session['recommended_showings']
    del session['share_link']
    return redirect('/')


@app.route("/explore", methods=['POST', 'GET'])
def explore():
    '''
    GET: in: mids, display: movie list 
    POST: in: chosen mid from form, out/carry: chosen mid
    '''
    # TODO: Need a "history" button, to viewing history and enable rating

    if request.method == 'POST':
        # user chooses movie
        chosen_mid = request.form.get("submit_button")
        # save movie id to session
        session['chosen_mid'] = chosen_mid
        print("====== chosen mid in session ======", session['chosen_mid'])
        return redirect('/preferences')
    else:
        # if 'mids' in request.args:
        #     mids = request.args['mids']
        if 'recommended_mids' in session:
            mids = session['recommended_mids']
        else:
            return render_template('explore.html', error="no mids")
        # retrieve movie list
        movies = []
        for mid in mids:
            movie = {}
            entity = get_movie(mid)
            movie['mid'] = mid
            movie['name'] = entity['name']
            movie['genre'] = entity['genre']
            # etc 
            movies.append(movie)       
        return render_template('explore.html', len=len(movies), movies=movies)


@app.route("/preferences", methods=['POST', 'GET'])
def preferences():
    '''
    GET: in: chosen mid, display: chosen movie, pre filled preference 
    POST: in: preference form, out: showing list, share link, carry: num tickets
    '''
    # TODO: share link

    if request.method == 'POST':
        # user submits preferences (select + self-input) 
        # can overwrite pre filled
        preference = {}
        preference['num_tickets'] = request.form.get('num_tickets')
        preference['time'] = request.form.get('time')
        preference['date'] = request.form.get('date')
        preference['zip'] = request.form.get('zip')
        preference['self_input'] = request.form.get('self_input')
        preference = augment_preference(preference)
        # save new preference to db 

        # etc 
        # for payment calc
        session['num_tickets'] = preference['num_tickets']
        print("====== num_tickets ======", session['num_tickets'])

        # filtering with rank
        showings = filter_shows(session['chosen_mid'], preference)

        # run seat selection algo
        for sid in showings:
            show = showings[sid]
            seats = select_seats(show)
            if not seats:
                del showings[sid]
            else:
                show['selected_seats'] = seats

        # generate share link
        share_link = 'https'

        session['recommended_showings'] = showings
        session['share_link'] = share_link
        # return redirect(url_for('.showings', showings=showings, share_link=share_link))
        return redirect('/showings')
    else:
        if 'chosen_mid' not in session:
            return render_template('preferences.html', error="no chosen_mid")
        # display chosen movie info
        movie = {}
        entity = get_movie(session['chosen_mid'])
        movie['name'] = entity['name']
        movie['genre'] = entity['genre']
        # etc 
        # return empty form
        # if logged in and have prev preference in db, pre fill form
        if 'user' in session:
            user_entity = session['user']
            preference = {}
            preference['num_tickets'] = user_entity['num_tickets']
            preference['time'] = user_entity['time']
            preference['date'] = user_entity['date']
            preference['zip'] = user_entity['zip']
            # etc 
        return render_template('preferences.html', movie=movie, preference=preference)


@app.route("/showings", methods=['POST', 'GET'])
def showings():
    '''
    GET: in: showing list, display: showing list
    POST: in: chosen sid from form, out payment amount, carry: chosen sid
    '''
    if request.method == 'POST':
        # user choses showing
        chosen_sid, price = request.form.get('sid_price').split('+')
        price = int(price)
        session['chosen_sid'] = chosen_sid
        # save showing info in db, for further rating 

        # payment
        amount = price * int(session['num_tickets'])
        return redirect(url_for('.payment', amount=amount))
    else:
        # if 'showings' in request.args:
        #     showings = request.args['showings']
        if 'recommended_showings' not in session:
            return render_template('showings.html', error='no showings')
        print("====== recommended_showings ======", session['recommended_showings'])
        showings = list(session['recommended_showings'].values())
        return render_template('showings.html', len=len(showings), showings=showings)

# do we need eg. another thread to listen and merge preferences??


@app.route("/payment", methods=['POST', 'GET'])
def payment():
    '''
    GET: in: payment amount, out/display: payinfo
    POST: in: payment form, out: db
    '''
    if request.method == 'POST':
        # user submits payment form 
        # just save the info to db for now
        return redirect('/success')
    else:
        if 'amount' in request.args:
            amount = request.args['amount']
        else:
            return render_template('payment.html', error="no payment amount")
        # if logged in and have prev payment info in db, pre fill form
        payinfo = {}
        payinfo['amount'] = amount
        if 'user' in session:    
            user_entity = session['user']
            payinfo['card_number'] = user_entity['card_number']    
            # etc 
        return render_template('payment.html', payinfo=payinfo)


@app.route("/success")
def success():
    return render_template('success.html')


@app.route("/history", methods=['POST', 'GET'])
def history():
    # TODO: retrieve viewing history, enable rating 
    return render_template('history.html')


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)