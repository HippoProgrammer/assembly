import asyncio # async functionality
import psycopg # postgres connector
import wa

class Database(Object):
    def __init__(self,connection_uri:str):
        self.connection_uri = connection_uri
    def setup(self):
        # database setup
        # check if the requisite tables already exist
        with psycopg.connect(self.connection_uri) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS NSQueue (
                    ID VARCHAR(63) PRIMARY KEY,
                    Council TINYINT CHECK (Council = 1 OR Council = 2),
                    Name VARCHAR(63) NOT NULL,
                    Category VARCHAR(63) NOT NULL,
                    Author VARCHAR(31) NOT NULL,
                    Coauthor_1 VARCHAR(31),
                    Coauthor_2 VARCHAR(31),
                    Coauthor_3 VARCHAR(31),
                    Legal BOOL
                    );
                    """) # create a table for storing queued proposal information, direct from the NS API
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS IFVQueue (
                    ID VARCHAR(63) PRIMARY KEY,
                    Thread INT NOT NULL,
                    IFVAuthor INT,
                    IFVLink VARCHAR(63)
                    );
                    """) # create a table for storing IFV information, such as assigned authors and regional positions
                conn.commit() # save changes to DB
    def add_proposal(proposal:wa.Proposal):
        with psycopg.connect(self.connection_uri) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO NSQueue (ID, Council, Name, Category, Author, Coauthor_1, Coauthor_2, Coauthor_3, Legal)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,proposal.values())
                conn.commit()