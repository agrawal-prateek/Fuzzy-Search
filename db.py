# Import Required Libraries
import json
import sqlite3


def build_db():
    """
    Function to build the database if not exist
    :return:
    """

    # Find the location of TSV file which contains the data
    with open('config.json', 'r') as configuration_file:
        configurations = json.loads(configuration_file.read())

    # Open TSV file and fetch the data
    with open(configurations['words_database'], 'r') as words_database:
        words = [(word.split()[0], int(word.split()[1])) for word in words_database.read().split('\n')[:-1]]

    # Sort the words alphabetically
    words.sort(key=lambda x: x[0])

    # Create the connection Object and create the database
    conn = sqlite3.connect('data/word_search.db')

    # Create a schema of Table
    conn.execute('create table fuzzy_search(word varchar primary key not null , frequency int default 0)')

    # Insert values in the table from words
    conn.executemany('insert into fuzzy_search(word, frequency) values (?,?)', words)

    # Commit the inserted values
    conn.commit()

    # Create the Indexes for fast Searching
    for i in range(97, 123):
        # Create index from a to z prefixes of words
        conn.execute(
            'create unique index {} on fuzzy_search(word,frequency) where word like "{}%"'
            .format(chr(i), chr(i))
        )
    # Close the connection Object
    conn.close()
