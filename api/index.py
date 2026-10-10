import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder="../templates")

# Di Vercel, penulisan file hanya diizinkan di /tmp/
if os.environ.get("VERCEL"):
    DATA_FILE = "/tmp/users.json"
else:
    DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "users.json")

def load_users():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_users(users):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving: {e}")
        return False

@app.route("/")
def catalog():
    return render_template("catalog.html")

@app.route("/cart")
def cart():
    return render_template("cart.html")

@app.route("/history")
def history():
    return render_template("history.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/api/register", methods=["POST"])
def api_register():
    try:
        data = request.get_json(silent=True) or {}
        username = data.get("username", "").strip().lower()
        email = data.get("email", "").strip().lower()
        phone = data.get("phone", "").strip()

        if not username or not phone:
            return jsonify({"success": False, "message": "Data tidak lengkap"}), 400

        users = load_users()
        for u in users:
            if u.get("username") == username:
                return jsonify({"success": False, "message": "Username sudah terdaftar!"}), 400
            if u.get("phone") == phone:
                return jsonify({"success": False, "message": "Nomor telepon sudah terdaftar!"}), 400

        new_user = {
            "id": f"usr-{len(users) + 1}",
            "name": data.get("name", "").strip(),
            "username": username,
            "email": email,
            "phone": phone,
            "gender": data.get("gender", ""),
            "password": data.get("password", "")
        }

        users.append(new_user)
        save_users(users)
        return jsonify({"success": True, "message": "Registrasi berhasil!", "user": new_user})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/login", methods=["POST"])
def api_login():
    try:
        data = request.get_json(silent=True) or {}
        identifier = data.get("identifier", "").strip().lower()
        phone = data.get("phone", "").strip()
        password = data.get("password", "")

        users = load_users()
        for u in users:
            match_id = (
                u.get("username") == identifier or 
                u.get("email") == identifier or 
                u.get("name", "").strip().lower() == identifier
            )
            if match_id and u.get("phone") == phone:
                if u.get("password") == password:
                    return jsonify({
                        "success": True,
                        "user": {
                            "name": u.get("name"),
                            "username": u.get("username"),
                            "email": u.get("email"),
                            "phone": u.get("phone"),
                            "gender": u.get("gender")
                        }
                    })
                else:
                    return jsonify({"success": False, "message": "Password salah!"}), 401

        return jsonify({"success": False, "message": "Akun belum terdaftar!"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)