import os
from flask import Flask, jsonify, send_file, request, Response, make_response
from flask_cors import CORS
from pathlib import Path
from lxml import etree
from functions import get_map_template, update_svg_template, get_pdf
import tempfile


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}}, 
     allow_headers=["Content-Type", "Authorization"], 
     methods=["OPTIONS", "HEAD", "GET", "POST", "PUT", "DELETE"])

PATH = "../client/public/"

def get_unique_filenames(folder_name):
    filenames = {}
    seen = set()
    folder_path = os.path.join(PATH, folder_name)

    for root, dirs, files in os.walk(folder_path):
        for file in files:  
            if not file.endswith(".svg"):
                continue
            filename = os.path.splitext(file)[0]
            name_parts = filename.split("-")
            if len(name_parts) > 0:
                name = name_parts[0]
                if name not in seen:
                    seen.add(name)
                    filenames[name] = 1
                else:
                    filenames[name] += 1

    return filenames

@app.route("/uniqueFilenames/<folder>")
def unique_filenames(folder):
    try:
        filenames = get_unique_filenames(folder)
        return jsonify(filenames)
    except Exception as e:
        return str(e), 500
        

@app.route("/uniqueTemplates/<folder>", methods=["POST"])
def get_unique_templates(folder):
    try:
        post_data = request.get_json()
        post_data["uniqueTemplates"][post_data["selectedTemplate"]]["forms"] = []
        for i in range(post_data["uniqueTemplates"][post_data["selectedTemplate"]]['countList']):
            path = os.path.join(PATH, folder, f"{post_data['selectedTemplate']}-{i+1}.svg")
            post_data["uniqueTemplates"][post_data["selectedTemplate"]]["forms"].append(get_map_template(path))
        return jsonify(post_data)
    except Exception as e:
        print("Eroor", e)
        return str(e), 500

@app.route("/static/<file>", methods = ['GET'])
def get_img(file):
    path = os.path.join(PATH, "static", file)
    if not os.path.exists(path):
        return "", 404
    
    return send_file(path, mimetype="image/png")

@app.route("/svg/<folder>/<file>", methods=['GET', 'POST', 'OPTIONS'])
def svg(folder, file):
    path = os.path.join(PATH, folder, file)
    if not os.path.exists(path):
        print("Not", path)
        return "", 404
    
    if request.method == "POST":
        post_data = request.get_json()
        with open(path) as card:
            root = etree.fromstring(card.read())
        index = int(path[-5]) - 1

        try:
            for e in update_svg_template(root, post_data, index):
                root.append(e)

            data_svg = etree.tostring(root)
            return Response(data_svg, mimetype='image/svg+xml')
        except Exception as e:
            print(e)
            return "", 500

    return send_file(path, mimetype="image/svg+xml")

@app.route("/pdf/<folder>", methods=["POST"])
def pdf(folder):
    path = os.path.join(PATH, folder)
    post_data = request.get_json()
    pdf_ = get_pdf(post_data, path)

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        pdf_.save()
        tmp.write(open('ex1.pdf', 'rb').read())

    response = make_response()
    response.data = open(tmp.name, 'rb').read()  # устанавливаем содержимое ответа
    response.headers['Content-Type'] = 'application/pdf'  # устанавливаем тип контента
    response.headers['Content-Disposition'] = 'attachment; filename=ex1.pdf'  # задаем имя файла и тип скачивания
    return response

if __name__ == "__main__":
    app.run(port=8081)