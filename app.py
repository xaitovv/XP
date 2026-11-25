import os
from flask import Flask, request, jsonify, send_from_directory, abort
from openai import OpenAI

app = Flask(__name__)

SYSTEM = "Sen mening shaxsiy yordamchimsan. Foydalanuvchi qaysi tilda yozsa, shu tilda javob ber (asosan o'zbekcha)."

# Navbat bilan sinab ko'riladi. Biri xato yoki limit bersa, keyingisiga o'tadi.
PROVAYDERLAR = [
    {"url": "https://generativelanguage.googleapis.com/v1beta/openai/",
     "kalit": os.environ.get("GEMINI_KEY"), "model": "gemini-2.0-flash"},
    {"url": "https://api.groq.com/openai/v1",
     "kalit": os.environ.get("GROQ_KEY"), "model": "llama-3.3-70b-versatile"},
    {"url": "https://openrouter.ai/api/v1",
     "kalit": os.environ.get("OPENROUTER_KEY"), "model": "meta-llama/llama-3.3-70b-instruct:free"},
]

FAYLLAR = {"index.html", "manifest.json", "sw.js", "icon-192.png", "icon-512.png"}


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/<path:nom>")
def fayl(nom):
    if nom not in FAYLLAR:
        abort(404)
    return send_from_directory(".", nom)


@app.route("/chat", methods=["POST"])
def chat():
    tarix = request.json.get("messages", [])[-20:]
    msgs = [{"role": "system", "content": SYSTEM}] + tarix
    for p in PROVAYDERLAR:
        if not p["kalit"]:
            continue
        try:
            c = OpenAI(base_url=p["url"], api_key=p["kalit"], timeout=40)
            r = c.chat.completions.create(model=p["model"], messages=msgs)
            return jsonify({"javob": r.choices[0].message.content})
        except Exception:
            continue
    return jsonify({"javob": "Hozir hamma xizmat band. Birozdan keyin urinib ko'ring."})
