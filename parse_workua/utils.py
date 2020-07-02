import json
import sqlite3


def create_db(db_fields):
    conn = sqlite3.connect('work_ua.db')
    c = conn.cursor()
    c.execute(f'CREATE TABLE work_ua {db_fields}')

    conn.commit()


def save_into_db(*args):
    conn = sqlite3.connect('work_ua.db')
    c = conn.cursor()
    c.execute(f'INSERT INTO work_ua VALUES {args}')

    conn.commit()
    conn.close()


def dict_factory(cursor, row):
    data = {}
    for idx, col in enumerate(cursor.description):
        data[col[0]] = row[idx]
    return data


def save_into_json():
    connection = sqlite3.connect("work_ua.db")
    connection.row_factory = dict_factory

    c = connection.cursor()
    c.execute("select * from work_ua")
    results = c.fetchall()
    with open('work_ua.json', 'w') as file:
        json.dump(results, file, ensure_ascii=False, indent=2)

    connection.close()
