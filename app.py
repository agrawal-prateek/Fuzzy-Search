
# Import Required Libraries
import json
import os
import sqlite3

from flask import *

from db import build_db

# Create Flask Object
app = Flask(__name__)


def fuzzy_search_start(word):
    """
    Function to search prefix matched words By Database using Indexing
    :param word: Requested word to be searched
    :return: A list object containing tuples of output words with field (word, frequency)
    """

    matched_words = []
    data = sorted(app.config['connection'].execute('select * from fuzzy_search where word like "{}%"'
                                                   .format(word)).fetchall(), key=lambda x: x[1], reverse=True)
    for row in data:
        if row[0] == word:
            matched_words.append((row[0], row[1]))
            break
    matched_words += sorted(data[:25], key=lambda x: len(x[0]))
    matched_words_count = 0
    for i in range(len(matched_words)):
        if matched_words[i][0] == word:
            matched_words_count += 1
        if matched_words_count == 2:
            del matched_words[i]
            break
    return matched_words


def fuzzy_search_end(word, length):
    """
    Words to search from database matching with word as pattern as suffix or in between of words
    :param word: Input word to be searched as pattern
    :param length: Total number of words needs to be searched
    :return: A list object containing tuples of output words with field (word, frequency)
    """
    data = sorted(
        app.config['connection'].execute('select * from fuzzy_search where word like "%{}%" and word not like "{}%"'
                                         .format(word, word)).fetchall(), key=lambda x: x[1], reverse=True)
    return sorted(data[:25 - length], key=lambda x: len(x[0]))


@app.route('/')
def index():
    """
    Route to render the Homepage
    """
    return render_template('index.html', title='Fuzzy Search')


@app.route('/search', methods=['GET'])
def fuzzy_search():
    """
    Search route which takes GET request
    :return: A Response Object in Json format, with response code 200
    """
    # Input the word from GET Request
    word = request.args.get('word').lower()

    # Search word for prefix matching
    start = fuzzy_search_start(word)

    # If prefix matching returns less than 25 rows, search for In between or End of the words
    if len(start) < 25:
        return json.dumps(start + fuzzy_search_end(word, len(start))), 200, {'ContentType': 'application/json'}
    # If prefix matching returns 25 or more rows, Convert to Json object and return
    return json.dumps(start), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    # If Database does not exist, build it from TSV file
    if not os.path.exists('data/word_search.db'):
        build_db()

    # Connect To Sqlite3 database
    app.config['connection'] = sqlite3.connect('data/word_search.db', check_same_thread=False)

    # Build the app's secret key
    app.config['secret_key'] = 'OpTmxdM5lrgNjoJVBbGPsBg98Jq7kwKL'

    # Host the application on port 8081 with Giving Remote access
    app.run(host='0.0.0.0', port='8081', debug=True)
