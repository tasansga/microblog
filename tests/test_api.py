# -*- coding: utf-8 -*-

"""
Test cases for API
"""

import unittest
import yaml
import microblog.api


class Api(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = microblog.api.get_app()
        cls.client = cls.app.test_client()

    def test_get_provider(self):
        response = self.client.get("/openapi/v1/messages")
        self.assertEqual(200, response.status_code)
        self.assertEqual("application/json", response.content_type)

    def test_openapi_schema(self):
        response = self.client.get("/openapi/v1/openapi.yaml")
        self.assertEqual(200, response.status_code)
        self.assertEqual("application/yaml", response.content_type)
        expected = yaml.dump(microblog.schema.SCHEMA_V1)
        self.assertEqual(expected, response.text)
