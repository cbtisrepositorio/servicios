
from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os, certifi

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")

# URI por defecto apuntando al cluster solicitado (puede ser reemplazada por variable MONGO_URI)
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://gerardotuz:7uppXMXlbZN8GOTN@cbtis272.qenkujr.mongodb.net/servicios?retryWrites=true&w=majority&appName=cbtis272"
)

# Conexión segura usando certifi (compatible con macOS/Windows/Render)
try:
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=10000)
    db = client.get_default_database()
    print("✅ Conectado correctamente a MongoDB Atlas.")
except Exception as e:
    print("❌ Error al conectar con MongoDB Atlas:", e)
    db = None

@app.route("/")
def index():
    datos = []
    if db is None:
        flash("Base de datos no conectada. Revisa tu MONGO_URI.", "danger")
    else:
        try:
            datos = db.servicios.find().sort("_id", -1)
        except Exception as e:
            flash(f"Error obteniendo datos: {e}", "danger")
    return render_template("index.html", datos=datos)

@app.route("/new", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        tipo = request.form.get("tipo", "").strip()
        alumno = request.form.get("alumno", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        estado = request.form.get("estado", "Pendiente").strip()

        if not tipo or not alumno:
            flash("Completa al menos 'Tipo de servicio' y 'Alumno'.", "warning")
            return redirect(url_for("create"))

        if db is not None:
            db.servicios.insert_one({
                "tipo": tipo,
                "alumno": alumno,
                "descripcion": descripcion,
                "estado": estado
            })
            flash("✅ Solicitud registrada.", "success")
        else:
            flash("Base de datos no conectada.", "danger")
        return redirect(url_for("index"))
    return render_template("create.html")

@app.route("/view/<id>")
def view(id):
    if db is None:
        flash("Base de datos no conectada.", "danger")
        return redirect(url_for("index"))
    dato = db.servicios.find_one({"_id": ObjectId(id)})
    if not dato:
        flash("Registro no encontrado.", "warning")
        return redirect(url_for("index"))
    return render_template("view.html", dato=dato)

@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
    if db is None:
        flash("Base de datos no conectada.", "danger")
        return redirect(url_for("index"))
    dato = db.servicios.find_one({"_id": ObjectId(id)})
    if not dato:
        flash("Registro no encontrado.", "warning")
        return redirect(url_for("index"))
    if request.method == "POST":
        tipo = request.form.get("tipo", "").strip()
        alumno = request.form.get("alumno", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        estado = request.form.get("estado", "Pendiente").strip()
        db.servicios.update_one({"_id": ObjectId(id)}, {"$set": {
            "tipo": tipo, "alumno": alumno, "descripcion": descripcion, "estado": estado
        }})
        flash("📝 Solicitud actualizada.", "info")
        return redirect(url_for("index"))
    return render_template("edit.html", dato=dato)

@app.route("/delete/<id>", methods=["POST"])
def delete(id):
    if db is None:
        flash("Base de datos no conectada.", "danger")
        return redirect(url_for("index"))
    db.servicios.delete_one({"_id": ObjectId(id)})
    flash("🗑️ Solicitud eliminada.", "secondary")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
