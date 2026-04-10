import asyncio # async functionality
import psycopg # postgres connector
import wa

class Database:
    def __init__(self,connection_uri:str):
        self.connection_uri = connection_uri
    async def setup(self):
        # database setup
        # check if the requisite tables already exist
        async with await psycopg.connect(self.connection_uri) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS NSQueue (
                    ID TEXT PRIMARY KEY,
                    Council SMALLINT CHECK (Council = 1 OR Council = 2),
                    Name TEXT NOT NULL,
                    Category TEXT NOT NULL,
                    Author TEXT NOT NULL,
                    Coauthors TEXT ARRAY[3],
                    Legal BOOL NOT NULL
                    );
                    """) # create a table for storing queued proposal information, direct from the NS API
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS IFVQueue (
                    ID VARCHAR(63) PRIMARY KEY,
                    Thread INT NOT NULL,
                    IFVAuthor INT,
                    IFVLink VARCHAR(63)
                    );
                    """) # create a table for storing IFV information, such as assigned authors and regional positions
                await conn.commit() # save changes to DB
    async def add_proposal(self,proposal:wa.Proposal):
        async with await psycopg.connect(self.connection_uri) as conn:
            async with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO NSQueue (ID, Council, Name, Category, Author, Coauthors, Legal)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ID) DO NOTHING;
                """,proposal.toSQLValues())
                conn.commit()
    async def get_queue(self):
        async with await psycopg.connect(self.connection_uri) as conn:
            async with conn.cursor() as cur:
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