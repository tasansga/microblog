#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Data models
"""

import logging
import datetime
import random
import sqlalchemy.orm
import sqlalchemy.sql.expression

Base = sqlalchemy.orm.declarative_base()


class MessageEntity(Base):
    """
    Abstracted message entity from a microblogging platform
    """

    @staticmethod
    def get_a_lot(session):
        """
        Simply return a random number of unordered messages
        """
        limit = random.randint(10, 50)
        result = session.scalars(
            sqlalchemy.select(MessageEntity)
            .order_by(sqlalchemy.sql.expression.func.random())
            .limit(limit)
        ).all()
        return result

    __tablename__ = "messageentity"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    datasource_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("datasource.id"), nullable=False
    )
    datasource = sqlalchemy.orm.relationship("DataSource")
    message = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    raw = sqlalchemy.orm.relationship(
        "RawSourceData", back_populates="entity", uselist=False
    )

    def __init__(self, datasource, message, raw):
        """
        Initialize a new message entity
        """
        self.datasource = datasource
        self.message = message
        self.raw = raw

    def asdict(self):
        """
        Get log-able dict representation of the object
        """
        return {
            "datasource": self.datasource.asdict(),
            "message": self.message,
            "raw": self.raw.asdict(),
        }


class RawSourceData(Base):  # pylint: disable=R0903
    """
    Raw, i.e. unparsed and unmanipulated data collected from sources
    """

    __tablename__ = "rawsourcedata"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    datasource_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("datasource.id"), nullable=False
    )
    datasource = sqlalchemy.orm.relationship("DataSource")
    entity_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("messageentity.id")
    )
    entity = sqlalchemy.orm.relationship(
        "MessageEntity", back_populates="raw", uselist=False
    )
    data = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)

    def __init__(self, datasource, data, timestamp=None):
        """
        Initialize a new object
        """
        logging.debug(
            "Initializing new RawSourceData object with datasource=%s and data=%s",
            datasource.asdict(),
            data,
        )
        self.datasource = datasource
        self.data = str(data)
        self.entity_id = None
        if timestamp is None:
            self.timestamp = datetime.datetime.now()
        else:
            self.timestamp = timestamp

    def asdict(self):
        """
        Get log-able dict representation of the object
        """
        return {
            "datasource": self.datasource.asdict(),
            "data": self.data,
            "entity_id": self.entity_id,
        }


class DataSource(Base):  # pylint: disable=R0903
    """
    Persisted definition and configuration for data sources
    """

    @staticmethod
    def get_by_name(session, name):
        """
        Get the datasource specified by name
        """
        result = session.scalars(
            sqlalchemy.select(DataSource).where(DataSource.name == name)
        ).first()
        return result

    __tablename__ = "datasource"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def __init__(self, name):
        """
        Initialize a new object with the given name
        """
        logging.debug("Initializing new DataSource object with name %s", name)
        self.name = name

    def get_raw_data(self, count=20):
        """
        Get unhandled raw data entries without assigned parsed entity
        """
        session = sqlalchemy.orm.Session.object_session(self)
        result = session.scalars(
            sqlalchemy.select(RawSourceData)
            .where(
                sqlalchemy.and_(
                    RawSourceData.datasource_id == self.id,
                    RawSourceData.entity_id == None,  # pylint: disable=C0121
                )
            )
            .order_by(RawSourceData.timestamp)
            .limit(count)
        ).all()
        logging.debug("Fetched raw data from database for %s: %s", self.name, result)
        return result

    def asdict(self):
        """
        Get log-able dict representation of the object
        """
        return {"name": self.name}
