#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse

import Database
import ThreadOrganizer

if __name__ == "__main__":
    ARG_PARSER = argparse.ArgumentParser(description="Manage ebook index")
    ARG_PARSER.add_argument(
        "--clean",
        action="store_true",
        help="Clean the DB")
    ARG_PARSER.add_argument(
        "--full",
        action="store_true",
        help="Download all books and put them into the DB, no matter what.")
    ARG_PARSER.add_argument(
        "--noaction",
        action="store_true",
        help="Don't download and push changes.")
    ARG_PARSER.add_argument(
        "--stats",
        action="store_true",
        help="Print stats on the local DB.")
    ARGS = ARG_PARSER.parse_args()
    if ARGS.clean:
        Database.clean()
    if not ARGS.noaction:
        ThreadOrganizer.generate(ARGS.full)
    if ARGS.stats:
        Database.stats()
