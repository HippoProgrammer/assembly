import asyncio # async functionality
import psycopg # postgres connector
import wa

class Database:
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
                    Council SMALLINT CHECK (Council = 1 OR Council = 2),
                    Name VARCHAR(63) NOT NULL,
                    Category VARCHAR(63) NOT NULL,
                    Author VARCHAR(63) NOT NULL,
                    Coauthor_1 VARCHAR(63),
                    Coauthor_2 VARCHAR(63),
                    Coauthor_3 VARCHAR(63),
                    Legal BOOL NOT NULL
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
    def add_proposal(self,proposal:wa.Proposal):
        with psycopg.connect(self.connection_uri) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO NSQueue (ID, Council, Name, Category, Author, Coauthor_1, Coauthor_2, Coauthor_3, Legal)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ID) DO NOTHING;
                """,proposal.toSQLValues())
                conn.commit()
    def get_queue(self):
        with psycopg.connect(self.connection_uri) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT * FROM NSQueue 
                WHERE Legal
                LIMIT 7;
                """)
                SQLqueue = cur.fetchall()
                conn.commit()
                queue = []
                for item in SQLqueue:
                    queue.append(wa.Proposal().fromSQLValues(item))
                return queue