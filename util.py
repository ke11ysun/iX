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


import re

def augment_preference(preference):
    # process natural language input
    # match keywords and extract features
    tokens = preference['self-input'].split()

    # show type (not in db) 
    show_type = '2D'
    SHOW_TYPES = {'2D', '3D', 'IMAX', 'DOLBY'}
    for token in tokens:
        if token in SHOW_TYPES:
            show_type = token
            break
    preference['show_type'] = show_type

    # cinema rate 
    rating = 0.0
    PATTERN = re.compile('\d+(\.\d+)?')
    ratings = re.findall(PATTERN, preference['self-input'])
    if len(ratings) > 0:
        rating = float(ratings[0])
    preference['rating'] = rating

    # cinema surrounding (not in db)
    hasRestaurant = False
    RESTAURANT = 'restaurant'
    if RESTAURANT in set(tokens):
        hasRestaurant = True
    preference['hasRestaurant'] = hasRestaurant

    # seat type (too complex)

    return preference

def select_seats(show, num_tickets, conn):
    # change show's seat map and update db
    # selected_seats = ['f1', 'g2']
    LEN_ROW = LEN_COL = 10
    ROW_IDS = 'abcdefghij' 
    COL_IDS = [str(i) for i in range(1, 11)]
    selected_seats = None
    seat_map = []

    # deserialize
    seats = show[-1].split(',')
    for row_start in range(0, len(seats), LEN_ROW):
        seat_map.append(''.join(seats[row_start : row_start + LEN_ROW])) # like '0110000000'

    # find continuous
    for i, row in enumerate(seat_map):
        if '0' * num_tickets in row:
            row_num = ROW_IDS[i]
            col_start_num = row.index('0' * num_tickets)
            col_nums = COL_IDS[col_start_num : col_start_num + num_tickets]
            selected_seats = [row_num + col_num for col_num in col_nums]
            break

    return selected_seats

def filter_shows(mname, preference, conn):
    # num_tickets, time, date, zip, show_type, rating, hasRestaurant
    cur = conn.cursor()
    cur.execute("SELECT mid FROM movies WHERE name = " + mname)
    mid = cur.fetchall()[0]

    query = "SELECT id, date, time, c.name, price, seat_map \
            FROM shows s, cinemas c \
            WHERE movie_id = {}\
                AND s.time >= {} \
                AND s.date = {} \
                AND s.show_type = {} \
                AND c.zip = {} \
                AND c.google_score >= {} \
                AND c.restaurant = {}".format(mid,
                                              preference['time'], 
                                              preference['date'], 
                                              preference['zip'], 
                                              preference['show_type'], 
                                              preference['rating'], 
                                              preference['hasRestaurant'])
    cur.execute(query)
    showings = cur.fetchall() # return list of tups

    # run seat selection algo
    for i, show in enumerate(showings):
        seats = select_seats(show, preference['num_tickets'], conn)
        if not seats:
            del showings[i]
        else:
            show['selected_seats'] = seats

    return showings



def get_user(username, password):
    return users[(username, password)]

def get_movie(mid):  
    return movies[mid]

def recommend(uid):
    mids = ['m001', 'm003']
    return mids
