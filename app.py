from flask import Flask, request, send_file, render_template, jsonify, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # Secret key for session management

# Hardcoded login credentials
USERNAME = "admin"
PASSWORD = "adminpanel123456"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the upload folder if it doesn't exist

# Ensure session expires when browser is closed
@app.before_request
def make_session_permanent():
    session.permanent = False

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == USERNAME and password == PASSWORD:
            session["user"] = username  # Store user session
            return redirect(url_for("file_list"))
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/file_list")
def file_list():
    if "user" not in session:  # Check if the user is logged in
        return redirect(url_for("login"))  # Redirect to login if not authenticated

    files = os.listdir(UPLOAD_FOLDER)  # List files in the upload folder
    return render_template("file_list.html", files=files)

import os

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No files uploaded"}), 400
        
        files = request.files.getlist("file")
        if not files:
            return jsonify({"error": "No selected files"}), 400

        for file in files:
            if file.filename == "":
                continue  # Skip files with no name

            # Get the folder path relative to the root
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save the file to the appropriate path
            file.save(file_path)

        return jsonify({"message": f"{len(files)} files uploaded successfully!"})

    return render_template("upload.html")



@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    if "user" not in session:  # Ensure user is logged in
        return jsonify({"error": "Unauthorized"}), 403

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
