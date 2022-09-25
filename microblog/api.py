#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Flask API
"""

import logging
import yaml
from flask import Flask, g, make_response, jsonify
from openapi_core.contrib.flask.decorators import FlaskOpenAPIViewDecorator
import microblog.db
import microblog.schema
import microblog.logconf
import microblog.model

# Initializes openapi decorator
openapi = FlaskOpenAPIViewDecorator.from_spec(microblog.schema.SPEC_V1)


def get_app():
    """
    Initialize the Flask app and attach routes and handlers
    """
    app = Flask(__name__)
    microblog.logconf.set_logging(microblog.logconf.LogConfig.CLI)

    def get_session():
        """
        Candy to set session in Flask's request global state
        """
        if "database" not in g:
            g.database = microblog.db.get_session()
        return g.database

    app.get_db = get_session

    @app.teardown_appcontext
    def close_connection(_exception):
        """
        On shutdown it's necessary to close an open database connection.
        """
        if "database" in g:
            try:
                g.database().remove()
            except Exception as err:  # pylint: disable=W0703
                logging.debug("Unexpected error when closing database: %s", err)

    @app.route("/openapi/v1/openapi.yaml")
    def openapi_schema():
        response = make_response(yaml.dump(microblog.schema.SCHEMA_V1))
        response.mimetype = "application/yaml"
        return response

    @app.route("/openapi/v1/messages")
    @openapi
    def messages():
        """
        Trivial API call to fetch a random batch of messages
        """
        with app.get_db() as session:
            messages = microblog.model.MessageEntity.get_a_lot(session)
            return jsonify(microblog.schema.generate_messages(messages))

    return app
