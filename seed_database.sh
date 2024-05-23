#!/bin/bash

rm db.sqlite3
rm -rf ./wishapi/migrations
python3 manage.py migrate
python3 manage.py makemigrations wishapi
python3 manage.py migrate wishapi
python3 manage.py loaddata users
python3 manage.py loaddata tokens
python3 manage.py loaddata wishlists
python3 manage.py loaddata priorities
python3 manage.py loaddata wishlist_items
python3 manage.py loaddata friends
python3 manage.py loaddata profiles
python3 manage.py loaddata pins
python3 manage.py loaddata purchases