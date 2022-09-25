#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Database set up and configuration
This prototype only supports SQLite as of now, but adding other
database engines should be as simple as adding their environment
config and configuring them here.
"""

import logging
import os
import sqlalchemy.orm
import microblog.model


def get_session(create_tables=True):
    """
    Initialize the database connection.
    """
    sqlite_path = os.environ.get("SQLITE_PATH", None)
    if sqlite_path is None or sqlite_path == "":
        raise ValueError("No valid database connection in config found!")
    connection = f"sqlite:///{sqlite_path}"
    logging.info("Connecting to: %s", connection)
    engine = sqlalchemy.create_engine(connection)
    if create_tables:
        base = microblog.model.Base
        base.metadata.create_all(engine)
    session = sqlalchemy.orm.Session(bind=engine, expire_on_commit=False)
    return session
