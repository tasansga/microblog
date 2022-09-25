#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
MicroBlog Aggregator demo pipeline CLI
"""

import sys
import os
import logging
import yaml
from docopt import docopt
import microblog.logconf
import microblog.api
import microblog.source.twitter

DOCOPT = """
MicroBlog Aggregator CLI

Usage:
  cli.py (-h | --help)
  cli.py serve
  cli.py openapi
  cli.py capture <source>
  cli.py transfer <source>

Commands:
  serve           Run the server daemon
  openapi         Print the OpenAPI schema
  capture         Start capturing data for the given source
  transfer        Process and transfer raw captured data from the given source 

Options:
  -h --help     Show this screen.

Environment variables:
    Logging:
        LOG_LEVEL           DEBUG, INFO, WARNING or ERROR (default: INFO)

    Connection to SQLite:
        SQLITE_PATH         Path to SQLite database file

    Capture specific:
        Twitter:
            MB_SOURCE_TWITTER_BEARER_TOKEN    Twitter bearer token
            MB_SOURCE_TWITTER_RULE            Twitter query operator

Return codes:
    0    OK
    1    Error
"""


def serve():
    """
    Start the API server
    """
    logging.debug("Starting flask app")
    microblog.api.get_app().run(host="0.0.0.0", port="5000")
    logging.debug("Flask app exited!")


def openapi():
    """
    Print the current OpenAPI schema as YAML
    """
    schema = yaml.dump(microblog.schema.SCHEMA_V1)
    print(schema)


def get_arguments_for_source(source_name):
    """
    Read environment variables for the given source name
    """
    src_args = {}
    for kname, kvalue in os.environ.items():
        if kname.startswith("MB_SOURCE_") and source_name.upper() in kname:
            src_args[kname] = kvalue
    logging.debug(
        "Found the following arguments for source %s: %s", source_name, src_args
    )
    return src_args


def capture(source, arguments):
    """
    Run capture operation on given source
    """
    # Here we're hardcoding the source for demonstration purposes,
    # in a real world use case we'd rather look them up dynamically.
    if source == "twitter":
        microblog.source.twitter.capture(arguments)
    else:
        logging.error("Invalid value for source: %s", source)
        raise ValueError(f"Unknown source: {source}")


def transfer(source):
    """
    Run transfer operation on given source
    """
    # Here we're hardcoding the source for demonstration purposes,
    # in a real world use case we'd rather look them up dynamically.
    if source == "twitter":
        microblog.source.twitter.transfer()
    else:
        logging.error("Invalid value for source: %s", source)
        raise ValueError(f"Unknown source: {source}")


def arg_runner(arguments):
    """
    CLI argument evaluator and runner
    """
    if arguments["serve"]:
        serve()
        return 0
    if arguments["openapi"]:
        openapi()
        return 0
    if arguments["capture"] and arguments["<source>"]:
        src_args = get_arguments_for_source(arguments["<source>"])
        capture(arguments["<source>"], src_args)
        return 0
    if arguments["transfer"] and arguments["<source>"]:
        transfer(arguments["<source>"])
        return 0
    logging.error("Encountered unknown argument constellation. This is a bug!")
    return 1


def entrypoint():
    """
    CLI application entry point
    """
    microblog.logconf.set_logging(microblog.logconf.LogConfig.CLI)
    logging.debug("Starting CLI")
    try:
        result = arg_runner(docopt(DOCOPT))
    except Exception as err:  # pylint: disable=W0703
        logging.error("Fatal error: %s", err)
        if logging.DEBUG >= logging.root.level:
            raise err
        result = 1
    logging.debug("Exiting CLI")
    return result


if __name__ == "__main__":
    sys.exit(entrypoint())
