from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from services.supabase_service import (
    insertar_jugador,
    obtener_jugadores,
    obtener_jugador_por_id,
    actualizar_estadisticas,
    insertar_inscripcion
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
CORS(app)

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
        data = {
            "name": request.form["name"],
            "email": request.form["email"],
            "position": request.form.get("position"),
            "gender": request.form.get("genero"),
            "team": request.form.get("equipo")
        }

        try:
            insertar_jugador(data)
            flash("Jugador agregado con éxito", "success")
        except Exception as e:
            flash(f"Error al agregar jugador: {str(e)}", "error")

        return redirect("/admin")

    jugadores = obtener_jugadores()
    return render_template("admin.html", jugadores=jugadores)

@app.route("/jugador/<int:id>", methods=["GET", "POST"])
def editar_estadisticas(id):
    if not session.get("admin_logged_in"):
        flash("Tenés que iniciar sesión", "error")
        return redirect("/login")

    if request.method == "POST":
        goals = request.form.get("goals", type=int)
        assistances = request.form.get("assistances", type=int)
        matches = request.form.get("matches", type=int)

        try:
            actualizar_estadisticas(id, {
                "goals": goals,
                "assistances": assistances,
                "matches": matches
            })
            flash("Estadísticas actualizadas", "success")
        except Exception as e:
            flash(f"Error: {e}", "error")

    jugador = obtener_jugador_por_id(id)
    return render_template("editar_estadisticas.html", jugador=jugador)

@app.route("/inscripcion", methods=["POST"])
def inscripcion():
    data = request.form or request.json

    inscripto = {
        "name": data.get("name"),
        "email": data.get("email"),
        "gender": data.get("genero"),
        "team": data.get("equipo"),
        "position": data.get("posicion")
    }

    if not all([inscripto["name"], inscripto["email"], inscripto["gender"], inscripto["team"]]):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    try:
        insertar_inscripcion(inscripto)
        return jsonify({"message": "Inscripción registrada con éxito"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/jugadores", methods=["GET"])
def jugadores():
    try:
        data = obtener_jugadores()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

@app.route("/test_supabase")
def test_supabase():
    try:
        data = obtener_jugadores()
        return jsonify({"ok": True, "jugadores": data}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
