import asyncio
import psycopg_pool
import psycopg.errors
import logging
import typing

class DBResponse:
    def __init__(self, success: bool, response: list | None):
        self.success = success
        self.response = response
    def __bool__(self) -> bool:
        return self.success
    def get_response(self) -> list | None:
        return self.response

class Database:
    def __init__(self, connection_uri: str) -> None:
        "Initialize a basic asynchronous pool of connections to a PostgreSQL database"
        self.logger = logging.getLogger(__name__) # give this instance the module-level logger

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
                conn.set_autocommit(autocommit)
                self.logger.debug('Connection fetched from pool')
                async with conn.cursor() as cur: # open a cursor
                    self.logger.debug('Cursor opened')

                    await cur.execute(query, params)
                    
                    self.logger.debug('Query executed successfully')

                    results = list(cur.fetchall())

                    self.logger.debug('Results fetched successfully')

                    success = True
        except psycopg_pool.PoolTimeout as e:
            self.logger.warning(e)
            self.connection_pool.check()
            success = False
        except psycopg.errors.Error as e:
            self.logger.error(e)
            success = False
        
        response = DBResponse(
            success = success,
            response = results
        )

        return response



class NSAssembly(Database):
    pass