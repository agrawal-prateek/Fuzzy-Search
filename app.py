import json
import os
import sqlite3

from flask import *

from db import build_db

app = Flask(__name__)


def fuzzy_search_start(word):
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
    data = sorted(
        app.config['connection'].execute('select * from fuzzy_search where word like "%{}%" and word not like "{}%"'
                                         .format(word, word)).fetchall(), key=lambda x: x[1], reverse=True)
    return sorted(data[:25 - length], key=lambda x: len(x[0]))


@app.route('/')
def index():
    return render_template('index.html', title='Fuzzy Search')


@app.route('/search', methods=['GET'])
def fuzzy_search():
    word = request.args.get('word').lower()
    start = fuzzy_search_start(word)
    if len(start) < 25:
        return json.dumps(start + fuzzy_search_end(word, len(start))), 200, {'ContentType': 'application/json'}
    return json.dumps(start), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    if not os.path.exists('data/word_search.db'):
        build_db()
    app.config['connection'] = sqlite3.connect('data/word_search.db', check_same_thread=False)
    app.config['secret_key'] = 'OpTmxdM5lrgNjoJVBbGPsBg98Jq7kwKL'
    app.run(host='0.0.0.0', port='8081', debug=True)
