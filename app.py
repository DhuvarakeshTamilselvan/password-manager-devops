import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "password-manager-demo-key"

# Temporary storage for demonstration
credentials = []


@app.route("/")
def home():
    version = os.environ.get("APP_VERSION", "v1")

    return render_template(
        "index.html",
        version=version,
        credentials=credentials if version in ["v2", "v3"] else [],
        can_view=version in ["v2", "v3"],
        can_delete=version == "v3"
    )


@app.route("/add", methods=["POST"])
def add_credentials():
    website = request.form.get("website", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not website or not username or not password:
        flash("Please fill in all fields.", "error")
        return redirect(url_for("home"))

    credentials.append({
        "id": max(
            (item["id"] for item in credentials),
            default=0
        ) + 1,
        "website": website,
        "username": username,
        "password": password
    })

    flash("Credentials added successfully.", "success")
    return redirect(url_for("home"))


@app.route("/delete/<int:credential_id>", methods=["POST"])
def delete_credentials(credential_id):
    if os.environ.get("APP_VERSION", "v1") != "v3":
        return "Delete is available only in Version 3.", 403

    for credential in credentials:
        if credential["id"] == credential_id:
            credentials.remove(credential)
            flash("Credential deleted successfully.", "success")
            break
    else:
        flash("Credential not found.", "error")

    return redirect(url_for("home"))


@app.route("/api/health")
def health():
    return {
        "application": "Password Manager",
        "version": os.environ.get("APP_VERSION", "v1"),
        "status": "running"
    }


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )