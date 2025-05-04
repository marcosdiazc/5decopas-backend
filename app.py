from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask_cors import CORS
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
CORS(app)  # permite peticiones desde el frontend externo

# Conexión a PostgreSQL
DB_PARAMS = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

def get_connection():
    return psycopg2.connect(**DB_PARAMS)

# Admin hardcodeado
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            flash("Sesión iniciada correctamente", "success")
            return redirect("/admin")
        else:
            flash("Usuario o contraseña incorrectos", "error")
            return redirect("/login")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    flash("Sesión cerrada", "info")
    return redirect("/")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin_logged_in"):
        flash("Tenés que iniciar sesión", "error")
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        position = request.form.get("position")
        genero = request.form.get("genero")
        equipo = request.form.get("equipo")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO jugadores (name, email, position, genero, equipo)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, position, genero, equipo))
        conn.commit()
        cur.close()
        conn.close()

        flash("Jugador agregado con éxito", "success")
        return redirect("/admin")

    return render_template("admin.html")

@app.route("/inscripcion", methods=["POST"])
def inscripcion():
    data = request.form or request.json

    name = data.get("name")
    email = data.get("email")
    genero = data.get("genero")
    equipo = data.get("equipo")
    posicion = data.get("posicion")

    if not all([name, email, genero, equipo]):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO jugadores (name, email, genero, equipo, position)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, genero, equipo, posicion))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Jugador registrado con éxito"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/jugadores", methods=["GET"])
def obtener_jugadores():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, genero, equipo, position FROM jugadores")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        jugadores = [
            {"name": r[0], "genero": r[1], "equipo": r[2], "posicion": r[3]} for r in rows
        ]
        return jsonify(jugadores), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

