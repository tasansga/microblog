#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Twitter Streaming API as data source
"""

import logging
import json
import tweepy
import sqlalchemy.orm
import microblog.db


def get_datasource(session):
    """
    Get the datasource associated with this implementation
    """
    datasource = microblog.model.DataSource.get_by_name(session, "twitter")
    if datasource is None:
        logging.debug("Persisting new DataSource for twitter")
        datasource = microblog.model.DataSource("twitter")
        session.add(datasource)
        session.commit()
    return datasource


class StreamingClient(tweepy.StreamingClient):
    """
    This class overrides tweepy's StreamingClient to implement our handlers
    """

    def on_tweet(self, tweet):
        """
        Data handler
        """
        logging.debug("Received tweet with id: %s", tweet.id)
        session = sqlalchemy.orm.Session.object_session(self.mb_datasource)
        raw_data = microblog.model.RawSourceData(
            self.mb_datasource, json.dumps(tweet.data)
        )
        session.add(raw_data)
        session.commit()
        logging.debug("Persisted tweet with id: %s", tweet.id)

    def on_errors(self, errors):
        """
        Error handler
        """
        logging.warning("Received errors: %s", errors)


def capture(config):
    """
    Entrypoint for this data source: Capture and save the raw twitter stream
    """
    if not "MB_SOURCE_TWITTER_BEARER_TOKEN" in config:
        raise ValueError("Invalid config, MB_SOURCE_TWITTER_BEARER_TOKEN not set!")
    if not "MB_SOURCE_TWITTER_RULE" in config:
        raise ValueError("Invalid config, MB_SOURCE_TWITTER_RULE not set!")
    logging.debug("Capturing twitter traffic with config: %s", config)
    streaming_client = StreamingClient(config["MB_SOURCE_TWITTER_BEARER_TOKEN"])
    with microblog.db.get_session() as session:
        streaming_client.mb_datasource = get_datasource(  # pylint: disable=W0201
            session
        )
        # We delete existing rules first so only the supplied, new rule is active.
        streaming_client.delete_rules(streaming_client.get_rules().data)
        rule_result = streaming_client.add_rules(
            tweepy.StreamRule(config["MB_SOURCE_TWITTER_RULE"])
        )
        logging.debug("Added rule: %s", rule_result)
        logging.info("Currently active rules: %s", streaming_client.get_rules())
        # Use this to read the real stream; for our purposes a sample is good enough though
        # streaming_client.filter()
        streaming_client.sample()
        session.commit()
    logging.debug("Finished capture")


def transform(raws):
    """
    Transform the list of raw data into entity messages
    """
    return [
        microblog.model.MessageEntity(raw.datasource, json.loads(raw.data)["text"], raw)
        for raw in raws
    ]


def transfer():
    """
    Entrypoint for the transfer routine: Fetch all entries from the source's
    stored raw data and transform and store them as message entities
    """
    with microblog.db.get_session() as session:
        datasource = get_datasource(session)
        while True:
            raw_data_sets = datasource.get_raw_data()
            if raw_data_sets is None or len(raw_data_sets) == 0:
                logging.debug("Exhausted raw data sets, finishing transfer")
                break
            logging.debug(
                "Starting transfer for %s entries in twitter", len(raw_data_sets)
            )
            entities = transform(raw_data_sets)
            session.add_all(entities)
            session.commit()
    logging.debug("Finished transfer")
