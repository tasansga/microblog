#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
OpenAPI schema definition
"""

import openapi_core


def generate_messages(messages):
    """
    Convert model messages into their OpenAPI representation
    """
    return {
        "messages": [
            {"datasource_name": message.datasource.name, "message": message.message}
            for message in messages
        ]
    }


def BasicError(message, code):  # pylint: disable=C0103
    """
    Create a BasicError dict as defined in schema.
    """
    return {"message": message, "code": code}


SCHEMA_V1 = {
    "openapi": "3.0.0",
    "info": {
        "version": "1.0",
        "title": "API",
        "description": "the API for querying microblog data",
    },
    "servers": [
        {"url": "http://localhost/openapi/v1"},
        {"url": "/openapi/v1"},
    ],
    "components": {
        "schemas": {
            "BasicError": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "code": {"type": "integer"},
                },
            },
            "MessageEntity": {
                "type": "object",
                "properties": {
                    "datasource_name": {"type": "string"},
                    "message": {"type": "string"},
                },
            },
        }
    },
    "paths": {
        "/messages": {
            "get": {
                "description": "Just an unsorted, messy batch of messages",
                "responses": {
                    "200": {
                        "description": "Successfully fetched message data",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "messages": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/MessageEntity"
                                            },
                                        },
                                    },
                                }
                            }
                        },
                    },
                },
            }
        }
    },
}

SPEC_V1 = openapi_core.create_spec(SCHEMA_V1)
