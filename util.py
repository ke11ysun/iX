u1 = {
        'username': 'kelly',
        'password': 'pswd',
        'uid': 'u001',
        'num_tickets': 2,
        'date': '2020-04-14', 
        'time': '4:00',
        'zip': 10044,
        'card_number': 'card0001'
    }

u2 = {
        'username': 'sjx',
        'password': 'hahaha',
        'uid': 'u002',
        'num_tickets': 3,
        'date': '2020-02-02', 
        'time': '0:00',
        'zip': 10044,
        'card_number': 'card0002'
    }

users = {
    ('kelly', 'pswd'): u1,
    ('sjx', 'hahaha'): u2
}

m1 = {
        'mid': 'm001',
        'name': 'Life of Brian',
        'genre': 'Comedy'
    }

m2 = {
        'mid': 'm002',
        'name': 'The Shining',
        'genre': 'Horror'
    }

m3 = {
        'mid': 'm003',
        'name': 'Lock Stock and Two Smoking Barriels',
        'genre': 'Drama'
    }

movies = {
    'm001': m1,
    'm002': m2,
    'm003': m3
}

s1 = {
    'sid': 's001',
    'date': '1900-01-01',
    'time': '0:00', 
    'cinema': 'AMC25',
    'price': 35
}

s2 = {
    'sid': 's002',
    'date': '1800-01-01',
    'time': '0:00', 
    'cinema': 'AMC34',
    'price': 80
}

showings = {
    's001': s1,
    's002': s2
}


def recommend(uid):
    mids = ['m001', 'm003']
    return mids

def augment_preference(preference):
    # process natural language input
    # match keywords and extract features
    return preference

def filter_shows(mid, preference):
    return showings

def select_seats(show):
    # change show's seat map and update db
    selected_seats = ['f1', 'g2']
    return selected_seats

def get_user(username, password):
    return users[(username, password)]

def get_movie(mid):  
    return movies[mid]