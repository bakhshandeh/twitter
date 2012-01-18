import psycopg2

conn = None

def getInstance():
    global conn
    if not conn:
        conn = psycopg2.connect("dbname=twitter user=postgres password=mehdireza host=127.0.0.1")
        conn.set_client_encoding("ISO-8859-1")
    return conn
