#!/usr/bin/env python3

import os
from mysql.connector import errors
from mysql.connector import pooling
import logging
from contextlib import closing

class ConnectionPool(object):

    conn_pool = None
    dbconfig = None
    
    @staticmethod
    def _init_db_config():          
                                    

         #Product database        
        ConnectionPool.dbconfig = {
            "user":os.environ.get('DATABASE_USER'),
            "password": os.environ.get('DATABASE_PASSWORD'),
            "host": os.environ.get('SQL_HOST'),
            "database": os.environ.get('DATABASE_NAME')
        }
        
    @staticmethod
    def get_conn():
        
        """ Get a connection from the pool. """
        conn = None
        
        try:
            if ConnectionPool.conn_pool is None:
                ConnectionPool._init_db_config()
                ConnectionPool.conn_pool = pooling.MySQLConnectionPool(pool_name="mypool",
                                                      pool_size=5,
                                                      **ConnectionPool.dbconfig)

                
                logging.info('Succeed to init connection pool. Pool name: %s. Pool size: %s.', 
                             str(ConnectionPool.conn_pool.pool_name), str(ConnectionPool.conn_pool.pool_size))

        except Exception as e:
            logging.error("Fail to init connection pool. Exception: " + str(e))

        conn = ConnectionPool.conn_pool.get_connection()
        
        return conn