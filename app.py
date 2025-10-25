from flask import Flask, request, send_file, jsonify
from io import BytesIO
import UnityPy
import logging

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "UnityPy API is running!"})

@app.route("/upload", methods=["POST"])
def upload():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files["file"]
        env = UnityPy.load(BytesIO(file.read()))

        deleted_scripts = []

        for obj in env.objects:
            if obj.type.name == "MonoBehaviour":
                data = obj.read()
                if data.name and "anticheat" in data.name.lower():
                    env.objects.remove(obj)
                    deleted_scripts.append(data.name)

        modified_asset = BytesIO(env.file.save())
        modified_asset.seek(0)
        logging.info(f"Deleted scripts: {deleted_scripts}")

        return send_file(modified_asset, as_attachment=True, download_name=file.filename)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
