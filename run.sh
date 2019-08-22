#!bin/bash

rm db.sqlite
python mock_database.py
python -m chessbot
