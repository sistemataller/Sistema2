
from flask import Flask, render_template, request, redirect, url_for, send_file
from datetime import datetime
import os
import sqlite3
from reportlab.pdfgen import canvas

app = Flask(__name__)
DB = "data/taller.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS motos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            numero_cliente TEXT,
            placa TEXT UNIQUE,
            marca TEXT,
            modelo TEXT,
            observaciones TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            moto_id INTEGER,
            fecha TEXT,
            descripcion TEXT,
            costo REAL,
            FOREIGN KEY(moto_id) REFERENCES motos(id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT,
            nombre TEXT,
            precio REAL
        )''')
        conn.commit()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/registro", methods=["POST"])
def registro():
    datos = (
        request.form["cliente"],
        request.form["numero_cliente"],
        request.form["placa"],
        request.form["marca"],
        request.form["modelo"],
        request.form["observaciones"]
    )
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO motos (cliente, numero_cliente, placa, marca, modelo, observaciones) VALUES (?, ?, ?, ?, ?, ?)", datos)
        conn.commit()
    return redirect(url_for("home"))

@app.route("/reporte/<placa>")
def reporte(placa):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM motos WHERE placa = ?", (placa,))
        moto = c.fetchone()
        c.execute("SELECT fecha, descripcion, costo FROM historial WHERE moto_id = ?", (moto[0],))
        historial = c.fetchall()

    archivo = f"data/reporte_{placa}.pdf"
    c = canvas.Canvas(archivo)
    c.drawString(100, 800, "Taller de motos EbenEzer")
    c.drawString(100, 785, "Dirección: barrio San pedro, col. Santa Isabel, Moncagua, San Miguel")
    c.drawString(100, 770, "Tel: 6117-6277")
    c.drawString(100, 750, f"Reporte de moto - Placa: {placa}")
    y = 730
    for h in historial:
        c.drawString(100, y, f"{h[0]} - {h[1]} - ${h[2]}")
        y -= 15
    c.save()
    return send_file(archivo, as_attachment=True)

if __name__ == "__main__":
    init_db()
    app.run()
