import json
import sqlite3
import os


def build_db():
    with open('config.json', 'r') as configuration_file:
        configurations = json.loads(configuration_file.read())
    with open(configurations['words_database'], 'r') as words_database:
        words = [(word.split()[0], int(word.split()[1])) for word in words_database.read().split('\n')[:-1]]
    words.sort(key=lambda x: x[0])

    conn = sqlite3.connect('data/word_search.db')
    conn.execute('create table fuzzy_search(word varchar primary key not null , frequency int default 0)')
    conn.executemany('insert into fuzzy_search(word, frequency) values (?,?)', words)
    conn.commit()
    for i in range(97, 123):
        conn.execute(
            'create unique index {} on fuzzy_search(word,frequency) where word like "{}%"'.format(chr(i), chr(i)))
    conn.close()
