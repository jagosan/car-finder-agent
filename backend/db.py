
import sqlite3
import os

DATABASE = os.environ.get('DATABASE_PATH', '/app/database/car_finder.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
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

    sql_create_feedback_table = """ CREATE TABLE IF NOT EXISTS feedback (
                                    id integer PRIMARY KEY,
                                    car_id integer NOT NULL,
                                    preference text NOT NULL,
                                    timestamp text NOT NULL,
                                    FOREIGN KEY (car_id) REFERENCES listings (id)
                                ); """
    c.execute(sql_create_listings_table)
    c.execute(sql_create_feedback_table)

    # Add new columns to listings table if they don't exist
    print("Attempting to add new columns to the listings table...")
    try:
        print("Adding image_url...")
        c.execute("ALTER TABLE listings ADD COLUMN image_url TEXT")
        print("image_url added.")
    except sqlite3.OperationalError:
        print("image_url column already exists.")
        pass # column already exists
    try:
        print("Adding exterior_color...")
        c.execute("ALTER TABLE listings ADD COLUMN exterior_color TEXT")
        print("exterior_color added.")
    except sqlite3.OperationalError:
        print("exterior_color column already exists.")
        pass # column already exists
    try:
        print("Adding interior_color...")
        c.execute("ALTER TABLE listings ADD COLUMN interior_color TEXT")
        print("interior_color added.")
    except sqlite3.OperationalError:
        print("interior_color column already exists.")
        pass # column already exists
    try:
        print("Adding drivetrain...")
        c.execute("ALTER TABLE listings ADD COLUMN drivetrain TEXT")
        print("drivetrain added.")
    except sqlite3.OperationalError:
        print("drivetrain column already exists.")
        pass # column already exists
    try:
        print("Adding has_accidents...")
        c.execute("ALTER TABLE listings ADD COLUMN has_accidents INTEGER")
        print("has_accidents added.")
    except sqlite3.OperationalError:
        print("has_accidents column already exists.")
        pass # column already exists
    print("Finished adding new columns.")

    conn.commit()
    conn.close()
