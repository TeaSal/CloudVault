import os
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from storage import get_s3_client, ensure_bucket, list_objects, upload_object, download_object, delete_object

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-local-demo-key")
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
BUCKET = os.getenv("S3_BUCKET", "cloudvault-files")

s3 = get_s3_client()
ensure_bucket(s3, BUCKET)

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/files")
def files():
    objects = list_objects(s3, BUCKET)
    total_bytes = sum(item["size_bytes"] for item in objects)
    return render_template("dashboard.html", objects=objects, total_bytes=total_bytes)

@app.post("/upload")
def upload():
    file = request.files.get("file")
    if not file or not file.filename:
        flash("Select a file before uploading.", "error")
        return redirect(url_for("files"))
    safe_name = secure_filename(file.filename)
    if not safe_name:
        flash("The selected filename is not valid.", "error")
        return redirect(url_for("files"))
    # Prefix each object key to avoid overwriting files with identical names.
    import uuid
    object_key = f"{uuid.uuid4().hex[:8]}_{safe_name}"
    try:
        upload_object(s3, BUCKET, object_key, file)
        flash(f"{safe_name} uploaded successfully.", "success")
    except Exception:
        app.logger.exception("Upload failed")
        flash("Upload failed. Check that MinIO is running and configured.", "error")
    return redirect(url_for("files"))

@app.get("/download/<path:key>")
def download(key):
    try:
        data, content_type, filename = download_object(s3, BUCKET, key)
        return send_file(BytesIO(data), mimetype=content_type,
                         as_attachment=True, download_name=filename)
    except Exception:
        app.logger.exception("Download failed")
        abort(404)

@app.post("/delete/<path:key>")
def delete(key):
    try:
        delete_object(s3, BUCKET, key)
        flash("File deleted successfully.", "success")
    except Exception:
        app.logger.exception("Delete failed")
        flash("Could not delete the selected file.", "error")
    return redirect(url_for("files"))

@app.errorhandler(413)
def too_large(_error):
    flash("File is too large. Maximum upload size is 25 MB.", "error")
    return redirect(url_for("files"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
