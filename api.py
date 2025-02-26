import json
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
                "content": "Vas a recibir una transcripción completa de una clase. Devuelve un JSON con la siguiente estructura: \{ titulo: 'titulo de la clase', materia: 'materia de la clase', texto: 'un resumen bien estructurado de la clase'\}",
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


app = Flask(__name__)
CORS(app)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/summary", methods=["POST"])
def summary():
    text = request.get_json()["text"]
    chat_response = chat_with_gpt(text)
    print(chat_response)
    data = json.loads(chat_response)
    title = data["titulo"]
    subject = data["materia"]
    text = data["texto"]
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO notes (texto, materia, titulo) VALUES (?, ?, ?)",
        (text, subject, title),
    )
    conn.commit()
    return jsonify({"message": "Data created successfully"}), 201


@app.route("/notes", methods=["GET"])
def get_all_notes():
    conn = get_db_connection()
    notes = conn.execute("SELECT * FROM notes").fetchall()
    print(notes)
    notes_list = [dict(note) for note in notes]  # Convert Row objects to dictionaries
    return jsonify(notes_list)


@app.route("/notes/<int:note_id>", methods=["GET"])
def get_note_by_id(note_id):
    conn = get_db_connection()
    note = conn.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
    if note is None:
        return jsonify({"message": "Note not found"}), 404
    return jsonify(dict(note))


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
