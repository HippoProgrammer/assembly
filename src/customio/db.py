import asyncio # async functionality
import psycopg # postgres connector
import psycopg_pool
import classes
import logging

# set up a logger
logger = logging.getLogger(__name__) # get the logger for this script

class Database:
    def __init__(self,connection_uri:str) -> None:
        """Create a new unconfigured Database object"""
        self.connection_uri = connection_uri # save the connection URI
        logger.debug('Connection URI received')

        self.connection_pool = psycopg_pool.AsyncConnectionPool(conninfo = connection_uri, min_size = 4, max_size = 16, open = False) # create a pool of connections for use later
        logger.info('ConnectionPool created')
    async def setup_all(self) -> None:
        """Configure a Database and make it ready to accept connections"""
        await self.connection_pool.open() # open the connection pool so connections can actually be made
        logger.info('ConnectionPool opened')

        # check if the requisite tables already exist, if not, create them
        async with self.connection_pool.connection() as conn: # get a connection from the pool
            logger.debug('DB connection opened from pool')
            async with conn.cursor() as cur: # open a cursor
                logger.debug('Cursor opened')
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
                logger.info('NSQueue table created')
                await cur.execute(""" 
                    CREATE TABLE IF NOT EXISTS IFVQueue (
                    ID TEXT PRIMARY KEY,
                    Name TEXT NOT NULL,
                    Thread BIGINT NOT NULL,
                    IFVAuthor BIGINT,
                    IFVLink TEXT
                    );
                    """) # create a table for storing IFV information, such as assigned authors and regional positions. 
                logger.info('IFVQueue table created')
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS BotPerms (
                    Kind TEXT PRIMARY KEY,
                    Identifier BIGINT NOT NULL
                    );
                    """) # create a table for storing perms
                logger.info('BotQueue table created')
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS ChannelReference (
                    Kind TEXT PRIMARY KEY,
                    Identifier BIGINT NOT NULL
                    );
                    """) # create a table for storing channels
                logger.info('ChannelReference table created')
                await cur.execute("""
                    CREATE INDEX IF NOT EXISTS NSQueue_ID_index ON NSQueue (ID);
                    """) # create relevant indexes on frequently-queried tables
                await cur.execute("""
                    CREATE INDEX IF NOT EXISTS IFVQueue_Author_index on IFVQueue (IFVAuthor);
                    """)
                logger.info('Indexes created')
                await conn.commit() # save changes to DB
    # NSQueue table
    async def nsqueue_add(self,proposal:classes.wa.Proposal) -> None:
        """Add a Proposal to the NSQueue"""
        try: # protect against PoolTimeouts
            async with self.connection_pool.connection() as conn: # get a connection from the pool
                logger.debug('DB connection opened from pool')
                async with conn.cursor() as cur: # open a cursor
                    logger.debug('Cursor opened')

                    await cur.execute("""
                    INSERT INTO NSQueue (ID, Council, Name, Category, Author, Coauthors, Legal, Quorum)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (ID) DO NOTHING;
                    """,proposal.toSQLValues()) # insert data into the table, but if it already exists ignore it
                    logger.info('Successful query')

                    await conn.commit()
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def nsqueue_get_by_id(self, id:str) -> classes.wa.Proposal:
        """Get a proposal by ID from the NSQueue"""
        try:
            async with self.connection_pool.connection() as conn: # get a connection from the pool
                logger.debug('DB connection opened from pool')
                async with conn.cursor() as cur: # open a cursor
                    logger.debug('Cursor opened')

                    await cur.execute("""
                    SELECT * FROM NSQueue
                    WHERE ID = %s;
                    """, [id]) # select all proposals with the supplied ID
                    logger.info('Successful query')

                    SQLproposal = await cur.fetchone() # fetch the proposal (as ID is unique there is only one)
                    proposal = classes.wa.Proposal().fromSQLValues(SQLproposal) # convert it into a Proposal object
                    return proposal
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def nsqueue_get_all_legal_by_council_limited(self, council = 1, limit = 7) -> list:
        """Get all proposals that are legal from the NSQueue, up to the specified limit"""
        try:
            async with self.connection_pool.connection() as conn: # get a connection from the pool
                logger.debug('DB connection opened from pool')
                async with conn.cursor() as cur: # open a cursor
                    logger.debug('Cursor opened')

                    await cur.execute("""
                    SELECT * FROM NSQueue 
                    WHERE Legal AND Council = %s 
                    LIMIT %s;
                    """, [council, limit]) # select all legal proposals, up to the queue limit of seven
                    logger.info('Successful query')

                    SQLqueue = await cur.fetchall() # fetch them all
                    queue = [] 
                    for item in SQLqueue:
                        queue.append(classes.wa.Proposal().fromSQLValues(item)) # convert them into a list of Proposal objects
                    return queue

        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    # IFVQueue table
    async def ifvqueue_add(self, ifv:classes.ifv.IFV) -> None:
        """Add an IFV to the IFVQueue"""
        try:
            async with self.connection_pool.connection() as conn: # get a connection from the pool
                logger.debug('DB connection opened from pool')
                async with conn.cursor() as cur: # open a cursor
                    logger.debug('Cursor opened')

                    await cur.execute("""
                    INSERT INTO IFVQueue (ID, Name, Thread, IFVAuthor, IFVLink)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (ID) DO NOTHING;
                    """, ifv.toSQLValues()) # insert data from IFV object
                    logger.info('Successful query')

                    await conn.commit() # save to DB
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def ifvqueue_check_exists_by_id(self, id:str) -> bool:
        """Check if an IFV exists in the IFVQueue with the specified ID"""
        try:
            async with self.connection_pool.connection() as conn:
                logger.debug('DB connection opened from pool')
                async with conn.cursor() as cur:
                    logger.debug('Cursor opened')

                    await cur.execute("""
                    SELECT 1 FROM IFVQueue
                    WHERE ID = %s
                    LIMIT 1;""", [id]) # return 1 or 0 depending on whether item exists

                    response = await cur.fetchone()

                    if response == None:
                        return False
                    else:
                        return True
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def ifvqueue_get_by_id(self, id:str) -> classes.ifv.IFV:
        """Get an IFV from the IFVQueue with the specified ID"""
        try:
            async with self.connection_pool.connection() as conn: # get a connection from the pool
                logger.debug('DB connection opened from pool')
                async with conn.cursor() as cur: # open a cursor
                    logger.debug('Cursor opened')

                    await cur.execute("""
                    SELECT * FROM IFVQueue
                    WHERE ID = %s;
                    """, [id]) # select all IFVs with the supplied ID
                    logger.info('Successful query')

                    SQLifv = await cur.fetchone() # fetch the IFV
                    ifv = classes.ifv.IFV().fromSQLValues(SQLifv) # convert to an IFV object
                    return ifv
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def ifvqueue_get_by_author(self, author:int) -> list:
        """Get all IFVs from the IFVQueue with the specified author"""
        try:
            async with self.connection_pool.connection() as conn: # get a connection from the pool
                logger.debug('DB connection opened from pool')
                async with conn.cursor() as cur: # open a cursor
                    logger.debug('Cursor opened')

                    await cur.execute("""
                    SELECT * FROM IFVQueue
                    WHERE IFVAuthor = %s;
                    """, [author]) # select all IFVs with the supplied author
                    logger.info('Successful query')

                    SQLifvs = await cur.fetchall() # fetch them all
                    ifvs = []
                    for item in SQLifvs:
                        ifvs.append(classes.ifv.IFV().fromSQLValues(item)) # convert to a list of IFVs
                    return ifvs
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def ifvqueue_get_unauthored_limited(self,limit = 7) -> list:
        """Get all IFVs from the IFVQueue with no author"""
        try:
            async with self.connection_pool.connection() as conn: # get a connection from the pool
                logger.debug('DB connection opened from pool')
                async with conn.cursor() as cur: # open a cursor
                    logger.debug('Cursor opened')

                    await cur.execute("""
                    SELECT * FROM IFVQueue
                    WHERE IFVAuthor IS NULL
                    LIMIT %s;
                    """,[limit]) # select all IFVs with no author up to the limit
                    logger.info('Successful query')

                    SQLifvs = await cur.fetchall() # fetch them all
                    ifvs = []
                    for item in SQLifvs:
                        ifvs.append(classes.ifv.IFV().fromSQLValues(item)) # convert to a list of IFVs
                    return ifvs
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def ifvqueue_update_author_by_id(self, id:str, author:int) -> None:
        """Change the IFVAuthor field on an IFV record with a specified ID"""
        try:
            async with self.connection_pool.connection() as conn: # get a connection from the pool
                logger.debug('DB connection opened from pool')
                async with conn.cursor() as cur: # open a cursor
                    logger.debug('Cursor opened')

                    await cur.execute("""
                    UPDATE IFVQueue
                    SET IFVAuthor = %s
                    WHERE ID = %s;
                    """, [author, id]) # update relevant records in the IFVQueue
                    logger.info('Successful query')

                    await conn.commit()
        except psycopg_pool.PoolTimeout:
            self.connection_self.connection_pool.check()
    async def ifvqueue_update_link_by_id(self, id:str, link:str) -> None:
        try:
            async with self.connection_pool.connection() as conn: # get a connection from the pool
                logger.debug('DB connection opened from pool')
                async with conn.cursor() as cur: # open a cursor
                    logger.debug('Cursor opened')
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
            async with self.connection_pool.connection() as conn: # get a connection from the pool
                logger.debug('DB connection opened from pool')
                async with conn.cursor() as cur: # open a cursor
                    logger.debug('Cursor opened')
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
            async with self.connection_pool.connection() as conn: # get a connection from the pool
                logger.debug('DB connection opened from pool')
                async with conn.cursor() as cur: # open a cursor
                    logger.debug('Cursor opened')
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
            async with self.connection_pool.connection() as conn: # get a connection from the pool
                logger.debug('DB connection opened from pool')
                async with conn.cursor() as cur: # open a cursor
                    logger.debug('Cursor opened')
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
            async with self.connection_pool.connection() as conn: # get a connection from the pool
                logger.debug('DB connection opened from pool')
                async with conn.cursor() as cur: # open a cursor
                    logger.debug('Cursor opened')
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
            async with self.connection_pool.connection() as conn: # get a connection from the pool
                logger.debug('DB connection opened from pool')
                async with conn.cursor() as cur: # open a cursor
                    logger.debug('Cursor opened')
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