import asyncio
import psycopg_pool
import psycopg.errors
import logging
import typing
import classes

class DBResponse:
    def __init__(self, success: bool, response: list | None):
        self.success = success
        self.response = response
    def __bool__(self) -> bool:
        return self.success
    def get_response(self) -> list | None:
        return self.response

class Database:
    def __init__(self, connection_uri: str, retry_on_fail = 3) -> None:
        "Initialize a basic asynchronous pool of connections to a PostgreSQL database"
        self.logger = logging.getLogger(__name__) # give this instance the module-level logger

        self.retry_on_fail = retry_on_fail

        self.connection_pool = psycopg_pool.AsyncConnectionPool(conninfo = connection_uri, min_size = 2, max_size = 16, open = False) # give this instance a connection pool to the DB
        self.logger.debug('Connection pool created')
    async def _open_connection_pool(self) -> None:
        await self.connection_pool.open() # opens the connection pool
        self.logger.debug('Connection pool opened')
    async def _close_connection_pool(self) -> None:
        await self.connection_pool.close() # closes the connection pool
        self.logger.debug('Connection pool closed')
    async def _query(self, query: str, params: tuple, autocommit = False) -> DBResponse:
        "Send raw SQL queries to the database"
        try:
            async with self.connection_pool.connection() as conn: # get a connection from the pool
                await conn.set_autocommit(autocommit)
                self.logger.debug('Connection fetched from pool')
                async with conn.cursor() as cur: # open a cursor
                    self.logger.debug('Cursor opened')

                    await cur.execute(query, params)

                    self.logger.debug('Query executed successfully')

                    results = list(await cur.fetchall())

                    self.logger.debug('Results fetched successfully')

                    response = DBResponse(
                        success = True,
                        response = results
                    )
        except psycopg_pool.PoolTimeout as e:
            self.logger.warning(e)
            await self.connection_pool.check()
            response = DBResponse(
                success = False,
                response = None
            )
        except psycopg.errors.Error as e:
            self.logger.error(e)
            response = DBResponse(
                success = False,
                response = None
            )
        return response

class NSAssembly(Database):
    async def ifvqueue_add(self, ifv:classes.IFV) -> DBResponse:
        return await super()._query(
            query = "INSERT INTO IFVQueue (ID, Name, Thread, IFVAuthor, IFVLink) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (ID) DO NOTHING;",
            params = ifv.toSQLValues()
        )
    async def ifvqueue_check_exists_by_id(self, id:str) -> DBResponse:
        return await super()._query(
            query = "SELECT 1 FROM IFVQueue WHERE ID = %s LIMIT 1;",
            params = tuple(id)
        )
    async def ifvqueue_get_by_id(self, id:str) -> DBResponse:
        return await super()._query(
            query = "SELECT * FROM IFVQueue WHERE ID = %s;",
            params = tuple(id)
        )
    async def ifvqueue_get_by_author(self, author:int) -> DBResponse:
        return await super()._query(
            query = "SELECT * FROM IFVQueue WHERE IFVAuthor = %s;",
            params = tuple(author)
        )
    async def ifvqueue_get_unauthored_limited(self, limit:int = 7) -> DBResponse:
        return await super()._query(
            query = "SELECT * FROM IFVQueue WHERE IFVAuthor IS NULL LIMIT %s;",
            params = tuple(limit)
        )
    async def ifvqueue_update_author_by_id(self, author:int, id:str) -> DBResponse:
        return await super()._query(
            query = "UPDATE IFVQueue SET IFVAuthor = %s WHERE ID = %s;",
            params = tuple([author, id])
        )
    async def ifvqueue_update_link_by_id(self, link:str, id:str) -> DBResponse:
        return await super()._query(
            query = "UPDATE IFVQueue SET IFVLink = %s WHERE ID = %s;",
            params = tuple([link, id])
        )
    async def ifvqueue_remove_author_link(self, id:str) -> DBResponse:
        return await super()._query(
            query = "UPDATE IFVQueue SET IFVAuthor = NULL, IFVLink = NULL;",
            params = tuple(id)
        )
