import numpy as np
import sqlite3
from sqlite3 import Error
import csv


def sql_connection():
	try:
		con = sqlite3.connect('iX.db')
		return con
	except Error:
		print(Error)

def sql_table(con):
	cursorObj = con.cursor()
	cursorObj.execute("CREATE TABLE movies(id integer PRIMARY KEY, name text, genre text, showing integer, year integer, IMDB real)")
	cursorObj.execute("CREATE TABLE shows(id integer PRIMARY KEY, movie_id integer, cinema_id integer, seat_map text, date_ integer, time_ text)")
	cursorObj.execute("CREATE TABLE cinemas(id integer PRIMARY KEY, name text, gmap text, addr text, trans text, google_score real)")
	con.commit()

def read_csv(file_name, to_num):
	with open(file_name, newline='') as f:
	    reader = csv.reader(f)
	    data = list(reader)
	to_db = []
	for i in data[1:]:
		for j in to_num:
			i[j] = float(i[j])
		to_db.append(tuple(i))
	return to_db

def to_database(movie_d, cinema_d, show_d):
	cursorObj = con.cursor()
	cursorObj.executemany("INSERT INTO movies (id, name, genre, showing, year, IMDB) VALUES (?, ?, ?, ?, ?, ?);", movie_d)
	cursorObj.executemany("INSERT INTO shows (id, movie_id, cinema_id, seat_map, date_, time_) VALUES (?, ?, ?, ?, ?, ?);", show_d)
	cursorObj.executemany("INSERT INTO cinemas (id, name, gmap, addr, trans, google_score) VALUES (?, ?, ?, ?, ?, ?);", cinema_d)
	con.commit()

'''
con = sql_connection()
sql_table(con)
movie_data = read_csv('movie.csv', [0, 3, 4, 5])
cinema_data = read_csv('cinema.csv', [0, 5])
show_data = read_csv('show.csv', [0, 1, 2, 4])
to_database(movie_data, cinema_data, show_data)
'''

