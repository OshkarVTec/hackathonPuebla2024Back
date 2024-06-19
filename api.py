from flask import Flask, jsonify
from openai import OpenAI
from flask import request, g
from flask_cors import CORS
import sqlite3

client = OpenAI()


def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def chat_with_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You will receive a full transcription of a class. Return a summary well structured of the class",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


app = Flask(__name__)
CORS(app)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/summary", methods=["POST"])
def summary():
    # response = chat_with_gpt(request.form['text'])
    content = request.form["text"]
    print(content)
    conn = get_db_connection()
    conn.execute("INSERT INTO notes (content) VALUES (?)", (content,))
    conn.commit()
    return jsonify({"message": "Data created successfully"}), 201


@app.route("/notes", methods=["GET"])
def get_all_notes():
    conn = get_db_connection()
    notes = conn.execute("SELECT * FROM notes").fetchall()
    print(notes)
    notes_list = [dict(note) for note in notes]  # Convert Row objects to dictionaries
    return jsonify(notes_list)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
