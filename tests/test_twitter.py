# -*- coding: utf-8 -*-

"""
Test cases for Twitter source
"""

import unittest
import microblog.db
import microblog.source.twitter


class Twitter(unittest.TestCase):
    def test_transform(self):
        pass

    def test_transfer(self):
        with microblog.db.get_session() as session:
            datasource = microblog.source.twitter.get_datasource(session)
            raws = [
                microblog.model.RawSourceData(
                    datasource, """{"text":"testmessage1"}"""
                ),
                microblog.model.RawSourceData(
                    datasource, """{"text":"testmessage2"}"""
                ),
            ]
            result = [cx.asdict() for cx in microblog.source.twitter.transform(raws)]
            self.assertEqual(
                [
                    {
                        "datasource": {"name": "twitter"},
                        "message": "testmessage1",
                        "raw": {
                            "datasource": {"name": "twitter"},
                            "data": '{"text":"testmessage1"}',
                            "entity_id": None,
                        },
                    },
                    {
                        "datasource": {"name": "twitter"},
                        "message": "testmessage2",
                        "raw": {
                            "datasource": {"name": "twitter"},
                            "data": '{"text":"testmessage2"}',
                            "entity_id": None,
                        },
                    },
                ],
                result,
            )

    def test_capture(self):
        pass
