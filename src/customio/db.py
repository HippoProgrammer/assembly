import asyncio # async functionality
import psycopg # postgres connector
import psycopg_pool
import classes

# set up a logger
logger = logging.getLogger(__name__) # get the logger for this script

class Database:
    def __init__(self,connection_uri:str):
        self.connection_uri = connection_uri
        self.connection_pool = psycopg_pool.AsyncConnectionPool(conninfo = connection_uri, min_size = 4, max_size = 16, open = False)
    async def setup_all(self):
        # database setup
        await self.connection_pool.open()
        # check if the requisite tables already exist
        async with self.connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS NSQueue (
                    ID TEXT PRIMARY KEY,
                    Council SMALLINT CHECK (Council = 1 OR Council = 2),
                    Name TEXT NOT NULL,
                    Category TEXT NOT NULL,
                    Author TEXT NOT NULL,
                    Coauthors TEXT ARRAY[3],
                    Legal BOOL NOT NULL,
                    Quorum BOOL NOT NULL
                    );
                    """) # create a table for storing queued proposal information, direct from the NS API
                await cur.execute(""" 
                    CREATE TABLE IF NOT EXISTS IFVQueue (
                    ID TEXT PRIMARY KEY,
                    Name TEXT NOT NULL,
                    Thread BIGINT,
                    IFVAuthor BIGINT,
                    IFVLink TEXT
                    );
                    """) # create a table for storing IFV information, such as assigned authors and regional positions. NOTE Thread should be NOT NULL in full release
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS BotPerms (
                    Kind TEXT PRIMARY KEY,
                    Identifier BIGINT NOT NULL
                    );
                    """) # create a table for storing perms
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS ChannelReference (
                    Kind TEXT PRIMARY KEY,
                    Identifier BIGINT NOT NULL
                    );
                    """)
                await cur.execute("""
                    CREATE INDEX NSQueue_ID_index ON NSQueue (ID);
                    """)
                await cur.execute("""
                    CREATE INDEX IFVQueue_Author_index on IFVQueue (IFVAuthor);
                    """)
                await conn.commit() # save changes to DB
    # NSQueue table
    async def nsqueue_add(self,proposal:classes.wa.Proposal):
        try:
            async with self.connection_pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    INSERT INTO NSQueue (ID, Council, Name, Category, Author, Coauthors, Legal, Quorum)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (ID) DO NOTHING;
                    """,proposal.toSQLValues())
                    await conn.commit()
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def nsqueue_get_by_id(self, id:str):
        try:
            async with self.connection_pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    SELECT * FROM NSQueue
                    WHERE ID = %s;
                    """, [id])
                    SQLproposal = await cur.fetchone()
                    proposal = classes.wa.Proposal().fromSQLValues(SQLproposal)
                    return proposal
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def nsqueue_get_all(self):
        try:
            async with self.connection_pool.connection() as conn:
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
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    # IFVQueue table
    async def ifvqueue_add(self, ifv:classes.ifv.IFV):
        try:
            async with self.connection_pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    INSERT INTO IFVQueue (ID, Name, Thread, IFVAuthor, IFVLink)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (ID) DO NOTHING;
                    """, ifv.toSQLValues())
                    await conn.commit()
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def ifvqueue_get_by_id(self, id:str):
        try:
            async with self.connection_pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    SELECT * FROM IFVQueue
                    WHERE ID = %s;
                    """, [id])
                    SQLifv = await cur.fetchone()
                    ifv = classes.ifv.IFV().fromSQLValues(SQLifv)
                    return ifv
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def ifvqueue_get_by_author(self, author:int):
        try:
            async with self.connection_pool.connection() as conn:
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
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def ifvqueue_get_unauthored_limited(self,limit = 7):
        try:
            async with self.connection_pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    SELECT * FROM IFVQueue
                    WHERE IFVAuthor IS NULL
                    LIMIT %s;
                    """,[limit])
                    SQLifvs = await cur.fetchall()
                    ifvs = []
                    for item in SQLifvs:
                        ifvs.append(classes.ifv.IFV().fromSQLValues(item))
                    return ifvs
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def ifvqueue_update_author_by_id(self, id:str, author:int):
        try:
            async with self.connection_pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    UPDATE IFVQueue
                    SET IFVAuthor = %s
                    WHERE ID = %s;
                    """, [author, id])
                    await conn.commit()
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def ifvqueue_update_link_by_id(self, id:str, link:str):
        try:
            async with self.connection_pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    UPDATE IFVQueue
                    SET IFVLink = %s
                    WHERE ID = %s;
                    """, [link, id])
                    await conn.commit()
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def ifvqueue_remove(self, id:str):
        try:
            async with self.connection_pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    DELETE FROM IFVQueue
                    WHERE ID = %s;
                    """, [id])
                    await conn.commit()
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    # BotPerms table
    async def botperms_add(self, permission:classes.auth.Permission):
        try:
            async with self.connection_pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    INSERT INTO BotPerms (Kind, Identifier)
                    VALUES (%s, %s)
                    ON CONFLICT (Kind) DO UPDATE SET Identifier = EXCLUDED.Identifier;
                    """, permission.toSQLValues())
                    await conn.commit()
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def botperms_get_by_kind(self, kind:str):
        try:
            async with self.connection_pool.connection() as conn:
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
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def channelref_add(self, channel:classes.auth.Channel):
        try:
            async with self.connection_pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    INSERT INTO ChannelReference (Kind, Identifier)
                    VALUES (%s, %s)
                    ON CONFLICT (Kind) DO UPDATE SET Identifier = EXCLUDED.Identifier;
                    """, channel.toSQLValues())
                    await conn.commit()
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def channelref_get_by_kind(self, kind:str):
        try:
            async with self.connection_pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                    SELECT Identifier FROM ChannelReference
                    WHERE Kind = %s;
                    """, [kind])
                    channel = await cur.fetchone() # note this method only allows for one permission of each type to be stored
                    if channel != None:
                        channel = int(channel[0])
                    else:
                        channel = 0
                    return channel
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def cleanup(self):
        await self.connection_pool.close()