#!/bin/bash

echo "Waiting for PostgreSQL..."
sleep 5

python init_db.py
python app.py