import asyncio # async functionality
import psycopg # postgres connector
import psycopg_pool
import classes

class Database:
    def __init__(self,connection_uri:str):
        self.connection_uri = connection_uri
        self.connection_pool = psycopg_pool.AsyncConnectionPool(conninfo = self.connection_uri, min_size = 2, max_size = 10, open = False)
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
                    ID TEXT PRIMARY KEY,
                    Thread BIGINT,
                    IFVAuthor BIGINT,
                    IFVLink TEXT
                    );
                    """) # create a table for storing IFV information, such as assigned authors and regional positions. NOTE Thread should be NOT NULL in full release
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS BotPerms (
                    Kind TEXT PRIMARY KEY,
                    Identifier BIGINT NOT NULL
                    );
                    """) # create a table for storing perms
                conn.commit() # save changes to DB
        await self.connection_pool.open()
    # NSQueue table
    async def nsqueue_add(self,proposal:classes.wa.Proposal):
        async with self.connection_pool as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    INSERT INTO NSQueue (ID, Council, Name, Category, Author, Coauthors, Legal)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (ID) DO NOTHING;
                    """,proposal.toSQLValues())
                    await conn.commit()
    async def nsqueue_get_by_id(self, id:str):
        async with self.connection_pool as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    SELECT * FROM NSQueue
                    WHERE ID = %s;
                    """, [id])
                    SQLproposal = await cur.fetchone()
                    proposal = classes.wa.Proposal().fromSQLValues(SQLproposal)
                    return proposal
    async def nsqueue_get_all(self):
        async with self.connection_pool as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    SELECT * FROM NSQueue 
                    WHERE Legal
                    LIMIT 7;
                    """)
                    SQLqueue = await cur.fetchall()
                    queue = []
                    for item in SQLqueue:
                        queue.append(classes.wa.Proposal().fromSQLValues(item))
                    return queue
    # IFVQueue table
    async def ifvqueue_add(self, ifv:classes.ifv.IFV):
        async with self.connection_pool as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    INSERT INTO IFVQueue (ID, Thread, IFVAuthor, IFVLink)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (ID) DO NOTHING;
                    """, ifv.toSQLValues())
                    await conn.commit()
    async def ifvqueue_get_by_id(self, id:str):
        async with self.connection_pool as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    SELECT * FROM IFVQueue
                    WHERE ID = %s;
                    """, [id])
                    SQLifv = await cur.fetchone()
                    ifv = classes.ifv.IFV().fromSQLValues(SQLifv)
                    return ifv
    async def ifvqueue_get_by_author(self, author:int):
        async with self.connection_pool as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    SELECT * FROM IFVQueue
                    WHERE IFVAuthor = %s;
                    """, [author])
                    SQLifvs = await cur.fetchall()
                    ifvs = []
                    for item in SQLifvs:
                        ifvs.append(classes.ifv.IFV().fromSQLValues(item))
                    return ifvs
    async def ifvqueue_get_unauthored(self):
        async with self.connection_pool as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    SELECT * FROM IFVQueue
                    WHERE IFVAuthor IS NULL;
                    """)
                    SQLifvs = await cur.fetchall()
                    ifvs = []
                    for item in SQLifvs:
                        ifvs.append(classes.ifv.IFV().fromSQLValues(item))
                    return ifvs
    async def ifvqueue_update_author_by_id(self, id:str, author:int):
        async with self.connection_pool as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    UPDATE IFVQueue
                    SET IFVAuthor = %s
                    WHERE ID = %s;
                    """, [author, id])
                    await conn.commit()
    async def ifvqueue_update_link_by_id(self, id:str, link:str):
        async with self.connection_pool as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    UPDATE IFVQueue
                    SET IFV = %s
                    WHERE ID = %s;
                    """, [link, id])
                    await conn.commit()
    async def ifvqueue_remove(self, id:str):
        async with self.connection_pool as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    DELETE FROM IFVQueue
                    WHERE ID = %s;
                    """, [id])
                    await conn.commit()
    # BotPerms table
    async def botperms_add(self, permission:classes.auth.Permission):
        async with self.connection_pool as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    INSERT INTO BotPerms (Kind, Identifier)
                    VALUES (%s, %s)
                    ON CONFLICT (Kind) DO UPDATE SET Identifier = EXCLUDED.Identifier;
                    """, permission.toSQLValues())
                    await conn.commit()
    async def botperms_get_by_kind(self, kind:str):
        async with self.connection_pool as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    SELECT Identifier FROM BotPerms
                    WHERE Kind = %s;
                    """, [kind])
                    permission = await cur.fetchone() # note this method only allows for one permission of each type to be stored
                    if permission != None:
                        permission = int(permission[0])
                    else:
                        permission = 0
                    return permission
    async def cleanup(self):
        await self.connection_pool.close()