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
    tokens = preference['self_input'].split()

    # show type 
    show_type = '2D'
    SHOW_TYPES = {'2D', '3D', 'IMAX', 'DOLBY'}
    for token in tokens:
        if token in SHOW_TYPES:
            show_type = token
            break
    preference['show_type'] = show_type

    # cinema rate 
    rating = 0.0
    PATTERN = re.compile("[-+]?\d*\.\d+|\d+")
    ratings = re.findall(PATTERN, preference['self_input'])
    if len(ratings) > 0:
        rating = float(ratings[0])
    preference['rating'] = rating

    # cinema surrounding 
    hasRestaurant = 0
    RESTAURANT = 'restaurant'
    if RESTAURANT in set(tokens):
        hasRestaurant = 1
    preference['hasRestaurant'] = hasRestaurant

    # map date to day
    # print(preference['date'])
    preference['day'] = int(preference['date'].split('-')[2]) % 7

    # print(preference)
    return preference

def select_seats(show, num_tickets, conn):
    # change show's seat map and update db
    # ROW_IDS = 'abcdefghij' 
    ROW_IDS = 'FGHIJKLMNP' # 造假
    COL_IDS = [str(i) for i in range(1, 11)]
    selected_seats = None

    seat_map = []
    rows = show['seat_map'].split(';')

    # find continuous
    for i, row in enumerate(rows):
        if '0' * num_tickets in row:
            row_num = ROW_IDS[i]
            col_start_num = row.index('0' * num_tickets)
            col_nums = COL_IDS[col_start_num : col_start_num + num_tickets]
            selected_seats = [row_num + col_num for col_num in col_nums]
            # update occupied
            row = row[:col_start_num] + '1' * num_tickets + row[col_start_num + num_tickets:]
            seat_map.append(row)
            start = i + 1 
            break       
    for i in range(start, len(rows)):
        seat_map.append(rows[i])
    # print(selected_seats)
    # print(seat_map)

    # store back to db  
    seat_map = ';'.join(seat_map)
    query = "UPDATE shows \
             SET seat_map = \"{}\" \
             WHERE id = {}".format(seat_map, show['sid']) 
    # print(query)
    cur = conn.cursor()
    cur.execute(query)

    # # test: reload check change
    # query = "SELECT * FROM shows WHERE id = {}".format(show['sid'])
    # cur.execute(query)
    # res = cur.fetchall()[0]
    # print(res)

    return selected_seats

def filter_shows(mname, preference, conn):
    # num_tickets, time, date, zip, show_type, rating, hasRestaurant
    preference = augment_preference(preference)

    # # test 
    # preference['show_type'] = '2D'
    # preference['time'] = '13:00'
    # preference['date'] = 3
    # preference['rating'] = 0.0
    # preference['hasRestaurant'] = 1

    cur = conn.cursor()
    query = "SELECT id FROM movies WHERE name = \"" + mname + "\""
    # print(query)
    cur.execute(query)
    mid = cur.fetchall()[0]['id']
    # print('mid:', mid)
    # print()

    query = "SELECT s.id as sid, date_ as day, time_ as time, c.name as cinema_name, c.addr as addr, price, seat_map \
            FROM shows s, cinemas c \
            WHERE movie_id = {}\
                AND s.time_ >= \"{}\" \
                AND s.date_ = {} \
                AND s.type = \"{}\" \
                AND c.zip = {} \
                AND c.google_score >= {} \
                AND c.restaurant = {}".format(mid,
                                              preference['time'], 
                                              preference['day'], 
                                              preference['show_type'],
                                              preference['zip'],  
                                              preference['rating'], 
                                              preference['hasRestaurant'])
    # print(query)
    cur.execute(query)
    showings = cur.fetchall() # return list of dict
    # print(len(showings))
    # pprint(showings[:5])

    # run seat selection algo
    showings = showings[:50] # display best 50 shows
    for i, show in enumerate(showings):
        # print(show)
        seats = select_seats(show, preference['num_tickets'], conn)
        if not seats:
            del showings[i]
        else:
            show['selected_seats'] = seats
            show['date'] = preference['date']

    return showings



def get_user(username, password):
    return users[(username, password)]

def get_movie(mid):  
    return movies[mid]

def get_movies(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM movies LIMIT 10")
    movies = cur.fetchall()
    return movies

def recommend(uid):
    mids = ['m001', 'm003']
    return mids



# test 
import sqlite3
from sqlite3 import Error
from pprint import pprint

def sql_connection():
    try:
        conn = sqlite3.connect('iX.db', check_same_thread=False)
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        print('DB connected')
        return conn
    except Error:
        print(Error)

if __name__ == "__main__":
    mname = "Trolls World Tour"
    conn = sql_connection()
    # preference = {'num_tickets': 3, 'time': "13:00", 'date': 3, 'zip': 10003, 'show_type': '2D', 'rating': 0.0, 'hasRestaurant': 1}
    preference = {'num_tickets': 3, 'time': "13:00", 'date': '04/22/2020', 'zip': '10003', 'self_input': 'hahah restaurant 4'}
    # preference = augment_preference(preference)
    showings = filter_shows(mname, preference, conn)
    print(showings[:2])