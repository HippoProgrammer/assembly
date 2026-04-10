import asyncio # async functionality
import psycopg # postgres connector
import classes

class Database:
    def __init__(self,connection_uri:str):
        self.connection_uri = connection_uri
    def setup_all(self):
        # database setup
        # check if the requisite tables already exist
        with psycopg.connect(self.connection_uri) as conn:
            with conn.cursor() as cur:
                cur.execute("""
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
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS IFVQueue (
                    ID VARCHAR(63) PRIMARY KEY,
                    Thread BIGINT NOT NULL,
                    IFVAuthor BIGINT,
                    IFVLink VARCHAR(63)
                    );
                    """) # create a table for storing IFV information, such as assigned authors and regional positions
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS BotPerms (
                    Kind TEXT PRIMARY KEY,
                    Identifier BIGINT NOT NULL
                    );
                    """) # create a table for storing perms
                conn.commit() # save changes to DB
    async def nsqueue_add(self,proposal:classes.wa.Proposal):
        async with await psycopg.AsyncConnection.connect(self.connection_uri) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                INSERT INTO NSQueue (ID, Council, Name, Category, Author, Coauthors, Legal)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ID) DO NOTHING;
                """,proposal.toSQLValues())
                await conn.commit()
    async def nsqueue_get_all(self):
        async with await psycopg.AsyncConnection.connect(self.connection_uri) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                SELECT * FROM NSQueue 
                WHERE Legal
                LIMIT 7;
                """)
                SQLqueue = await cur.fetchall()
                await conn.commit()
                queue = []
                for item in SQLqueue:
                    queue.append(classes.wa.Proposal().fromSQLValues(item))
                return queue
    async def botperms_add(self, permission:classes.auth.Permission):
        async with await psycopg.AsyncConnection.connect(self.connection_uri) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                INSERT INTO BotPerms (Kind, Identifier)
                VALUES (%s, %s)
                ON CONFLICT (Kind) DO UPDATE SET Identifier = EXCLUDED.Identifier;
                """, permission.toSQLValues())
                await conn.commit()
    async def botperms_get_by_kind(self, kind:str):
        async with await psycopg.AsyncConnection.connect(self.connection_uri) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                SELECT Identifier FROM BotPerms
                WHERE Kind = %s;
                """, [kind])
                permission = await cur.fetchone() # note this method only allows for one permission of each type to be stored
                await conn.commit()
                if permission != None:
                    permission = int(permission[0])
                else:
                    permission = 0
                return permission