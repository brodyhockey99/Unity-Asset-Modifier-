from flask import Flask, request, jsonify
import UnityPy
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Unity Asset Modifier API is running!"

@app.route("/extract", methods=["POST"])
def extract_assets():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    temp_path = os.path.join("/tmp", file.filename)
    file.save(temp_path)

    env = UnityPy.load(temp_path)
    extracted = []
    for obj in env.objects:
        if obj.type.name in ["Texture2D", "AudioClip", "TextAsset"]:
            data = obj.read()
            extracted.append({"name": data.name, "type": obj.type.name})

    return jsonify({"extracted_assets": extracted})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
