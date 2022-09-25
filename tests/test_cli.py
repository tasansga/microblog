# -*- coding: utf-8 -*-

"""
Test cases for CLI
"""

import unittest
import microblog.cli

ARGS = {
    "--help": False,
    "--version": False,
    "<source>": None,
    "capture": False,
    "openapi": True,
    "serve": False,
    "transfer": False,
}


class Cli(unittest.TestCase):
    def test_openapi(self):
        arguments = ARGS.copy()
        arguments["openapi"] = True
        result = microblog.cli.arg_runner(arguments)
        self.assertEqual(0, result)

    def test_capture(self):
        pass

    def test_serve(self):
        pass

    def test_transfer(self):
        pass
