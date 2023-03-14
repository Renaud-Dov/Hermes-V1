#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved

from os import environ

import psycopg2

conn = psycopg2.connect(
    host=environ.get("DB_HOST"),
    database=environ.get("DB_DATABASE"),
    user=environ.get("DB_USERNAME"),
    password=environ.get("DB_PASSWORD")
)

cursor = conn.cursor()

def execute_sql():
    try:
        conn.commit()
    except Exception as e:
        print(e)


def get_ticket_nb(id: int) -> int:
    cursor.execute("SELECT * FROM tickets WHERE ticket_id = %s", (str(id),))
    rows = cursor.fetchall()
    if len(rows) == 0:
        return -1
    return rows[0][0]

def get_id_ticket(id: int) -> int:
    cursor.execute("SELECT * FROM tickets WHERE id = %s", (id,))
    rows = cursor.fetchall()
    if len(rows) == 0:
        return -1
    return rows[0][1]

def add_ticket(id: int, user_id: int):
    cursor.execute("INSERT INTO tickets (ticket_id, by) VALUES (%s, %s)", (str(id), str(user_id)))
    execute_sql()