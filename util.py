import re

def augment_preference(preference):
    # process natural language input
    # match keywords and extract features
    tokens = preference['self_input'].split()

    # show type 
    show_type = '2D'
    SHOW_TYPES = {'2D':'2D', '2d': '2D', 'IMAX':'iMax', 'imax':'iMax'}
    for token in tokens:
        if token in SHOW_TYPES:
            show_type = SHOW_TYPES[token]
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
    preference['day'] = int(preference['date'].split('-')[2]) % 7

    print('preference:\n', preference)
    return preference

def select_seats(show, num_tickets, conn):
    # change show's seat map and update db
    # ROW_IDS = 'abcdefghij' 
    ROW_IDS = 'FGHIJKLMNP' # 造假
    COL_IDS = [str(i) for i in range(1, 11)]
    selected_seats = None

    seat_map = []
    rows = show['seat_map'].split(';')
    start = 0

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

    # # store back to db  
    # seat_map = ';'.join(seat_map)
    # query = "UPDATE shows \
    #          SET seat_map = \"{}\" \
    #          WHERE id = {}".format(seat_map, show['sid']) 
    # cur = conn.cursor()
    # cur.execute(query)
    # conn.commit()

    # # test: reload check change
    # query = "SELECT seat_map FROM shows WHERE id = {}".format(show['sid'])
    # cur.execute(query)
    # res = cur.fetchall()[0]
    # print('retrieve updated seatmap from db', res)

    return selected_seats

def filter_shows(mname, preference, conn):
    # num_tickets, time, date, zip, show_type, rating, hasRestaurant
    preference = augment_preference(preference)

    cur = conn.cursor()
    query = "SELECT id FROM movies WHERE name = \"" + mname + "\""
    cur.execute(query)
    mid = cur.fetchall()[0]['id']

    query = "SELECT s.id as sid, date_ as day, time_ as time, c.name as cinema_name, c.addr as addr, price, seat_map \
            FROM shows s, cinemas c \
            WHERE movie_id = {}\
                AND s.cinema_id = c.id\
                AND s.time_ >= \"{}\" \
                AND s.date_ BETWEEN {} AND {}\
                AND s.type = \"{}\" \
                AND c.zip BETWEEN {} AND {}\
                AND c.google_score >= {} \
                AND c.restaurant = {}".format(mid,
                                              preference['time'], 
                                              preference['day'], preference['day'] + 3, 
                                              preference['show_type'],
                                              str(int(preference['zip']) - 30), str(int(preference['zip']) + 30),  
                                              preference['rating'], 
                                              preference['hasRestaurant'])
    cur.execute(query)
    showings = cur.fetchall() # return list of dict
    print('Number of shows before seat selection:', len(showings))
    
    # run seat selection algo
    showings = showings[:50] # display best 50 shows
    for i, show in enumerate(showings):
        seats = select_seats(show, preference['num_tickets'], conn)
        if not seats:
            del showings[i]
        else:
            show['selected_seats'] = seats
            show['date'] = preference['date']
    print('Number of shows after seat selection:', len(showings))

    return showings

def get_movies(conn, mids=(1, 6, 8, 12, 14, 15, 21, 28, 33, 44, 54, 107, 352)):
    cur = conn.cursor()
    query = "SELECT * FROM movies WHERE id in {}".format(mids)
    cur.execute(query)
    movies = cur.fetchall()
    return movies

def safe_cast(form, key, default, try_int=False):
    try:
        if try_int: return int(form[key])
        else: return form[key] if form[key] != "" else default
    except:
        return default

def update_purchase(conn, preference):
    cur = conn.cursor()
    cur.execute("UPDATE purchase SET num_tickets = {}, \
                                    show_time = '{}', \
                                    show_date = '{}', \
                                    zip = '{}', \
                                    self_input = '{}' WHERE id = 1".format(
                                        preference["num_tickets"], 
                                        preference["time"], 
                                        preference["date"], 
                                        preference["zip"], 
                                        preference["self_input"]))
    conn.commit()

def get_purchase(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM purchase LIMIT 1")
    return cur.fetchall()


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
    # mname = "Trolls World Tour"
    conn = sql_connection()
    # preference = {'num_tickets': 3, 'time': "13:00", 'date': '2020-07-07', 'zip': '10003', 'self_input': '4 star cinema'} # basic case
    # # preference = {'num_tickets': 5, 'time': "18:00", 'date': '2020-05-05', 'zip': '10044', 'self_input': 'IMAX restaurant'} # more strict constraint: 0505:1, 0507: 6 
    # # preference = {'num_tickets': 8, 'time': "20:00", 'date': '2020-05-07', 'zip': '10010', 'self_input': 'aisle seats'} # seat selection: 0505: 13 -> 12, 0507: 21 -> 18 
    # showings = filter_shows(mname, preference, conn)
    # print(showings[:2])
