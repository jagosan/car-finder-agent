import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn):
    """ create a table from the create_table_sql statement """
    try:
        sql_create_listings_table = """ CREATE TABLE IF NOT EXISTS listings (
                                        id integer PRIMARY KEY,
                                        make text NOT NULL,
                                        model text NOT NULL,
                                        year integer NOT NULL,
                                        price real NOT NULL,
                                        mileage integer,
                                        vin text UNIQUE,
                                        location text,
                                        url text NOT NULL UNIQUE,
                                        source_site text,
                                        scraped_timestamp text NOT NULL
                                    ); """
        c = conn.cursor()
        c.execute(sql_create_listings_table)
    except Error as e:
        print(e)

def insert_listing(conn, listing):
    """
    Create a new listing into the listings table
    :param conn:
    :param listing:
    :return: project id
    """
    sql = ''' INSERT OR IGNORE INTO listings(make,model,year,price,mileage,vin,location,url,source_site,scraped_timestamp)
              VALUES(?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, listing)
    conn.commit()
    return cur.lastrowid

def get_all_listings(conn):
    """
    Query all rows in the listings table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM listings")

    rows = cur.fetchall()

    for row in rows:
        print(row)

if __name__ == '__main__':
    db_file = "car_finder.db"

    conn = create_connection(db_file)
    if conn is not None:
        create_table(conn)

        # create a new listing
        listing = ('Toyota', 'Camry', 2022, 25000, 15000, '123456789ABCDEFGH', 'Los Angeles, CA', 'http://example.com/car1', 'example.com', '2025-10-03 12:00:00')
        insert_listing(conn, listing)

        get_all_listings(conn)

        conn.close()
    else:
        print("Error! cannot create the database connection.")
