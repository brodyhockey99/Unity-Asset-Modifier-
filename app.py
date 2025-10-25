from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import UnityPy
import os

app = Flask(__name__)
CORS(app)

# HTML for upload page
UPLOAD_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Unity Asset Modifier</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background: #111; color: #fff; }
        h1 { color: #00ffcc; }
        form { margin-top: 50px; }
        input[type=file] { padding: 10px; border-radius: 10px; background: #222; color: #fff; border: 1px solid #00ffcc; }
        button { padding: 10px 20px; margin-top: 10px; border: none; background: #00ffcc; color: #000; border-radius: 8px; cursor: pointer; }
        button:hover { background: #00ffaa; }
        .results { margin-top: 40px; text-align: left; display: inline-block; }
        .asset-item { background: #222; padding: 8px; border-radius: 6px; margin: 5px 0; }
    </style>
</head>
<body>
    <h1>Unity Asset Modifier</h1>
    <p>Upload any Unity .assets or .bundle file to extract its contents</p>
    <form id="uploadForm" enctype="multipart/form-data">
        <input type="file" name="file" accept=".assets,.bundle" required><br>
        <button type="submit">Upload & Extract</button>
    </form>
    <div class="results" id="results"></div>

    <script>
    document.getElementById("uploadForm").onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        document.getElementById("results").innerHTML = "<p>Processing...</p>";
        const res = await fetch("/extract", { method: "POST", body: formData });
        const data = await res.json();
        const container = document.getElementById("results");
        container.innerHTML = "<h3>Extracted Assets:</h3>";
        if (data.extracted_assets && data.extracted_assets.length > 0) {
            data.extracted_assets.forEach(a => {
                const el = document.createElement("div");
                el.className = "asset-item";
                el.textContent = `${a.name} (${a.type})`;
                container.appendChild(el);
            });
        } else {
            container.innerHTML += "<p>No assets found or unsupported file.</p>";
        }
    };
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(UPLOAD_PAGE)

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
        if obj.type.name in ["Texture2D", "AudioClip", "TextAsset", "Shader", "GameObject"]:
            try:
                data = obj.read()
                extracted.append({"name": data.name, "type": obj.type.name})
            except Exception:
                continue

    return jsonify({"extracted_assets": extracted})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
