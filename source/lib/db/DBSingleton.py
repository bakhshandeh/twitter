import psycopg2

conn = None

def getInstance():
    global conn
    if not conn:
        conn = psycopg2.connect("dbname=twitter user=postgres password=mehdireza")
        conn.set_client_encoding("ISO-8859-1")
    return conn
