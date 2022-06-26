from typing import Dict, List, Tuple
import sqlite3


conn = sqlite3.connect('finance.db')
cursor = conn.cursor()


def insert(table: str, column_values: Dict):
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    cursor.executemany(
        f'INSERT INTO {table}'
        f'({columns})'
        f'VALUES ({placeholders})',
        values)
    conn.commit()


def fetchall(table: str, columns: List[str]) -> List[Tuple]:
    columns_joined = ", ".join(columns)
    cursor.execute(f'SELECT {columns_joined} FROM {table}')
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def delete(table: str, row_id: int) -> None:
    row_id = int(row_id)
    cursor.execute(f'delete from {table} where id={row_id}')
    conn.commit()


def get_cursor():
    return cursor


def _init_db():
    sqlite_create_table_query = '''
    
    create table budget(
    name varchar(255) primary key,
    daily_limit integer
    );

    create table category(
    name varchar(255),
    is_base_expense boolean,
    aliases text
    );

    create table expense(
    id integer primary key,
    amount integer,
    created datetime,
    category_name integer,
    raw_text text,
    FOREIGN KEY(category_name) REFERENCES category(name)
    );

    insert into category (name, is_base_expense, aliases)
    values
    ("products", true, "food"),
    ("coffee", true, ""),
    ("dinner", true, "lunch, business lunch"),
    ("cafe", true, "restaurant, mcdonalds, fastfood, kfc"),
    ("transport", false, "fuel, car, metro"),
    ("taxi", false, "yandex taxi, uber"),
    ("phone", false, "mts, a1, life"),
    ("books", false, "book"),
    ("internet", false, "inet"),
    ("subscriptions", false, "subs"),
    ("other", true, "");

    insert into budget(name, daily_limit) values ('base', 500);
    '''
    cursor.executescript(sqlite_create_table_query)
    conn.commit()


def check_db_exists():
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' AND name='expense'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()


check_db_exists()
