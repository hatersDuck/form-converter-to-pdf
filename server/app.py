import os
from flask import Flask, jsonify, send_file, request, Response, make_response
from flask_cors import CORS
from lxml import etree
from functions import get_map_template, update_svg_template, get_pdf
import tempfile
from const import PATH, PATH_STATIC, IP
from PIL import Image
import io
from datetime import datetime


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, 
     allow_headers=["Content-Type", "Authorization"], 
     methods=["OPTIONS", "HEAD", "GET", "POST", "PUT", "DELETE"])

@app.route('/compress', methods=['POST'])
def compress_image():
    try:
        file = request.files['image']

        img = Image.open(file)
        img = img.convert('RGB')  # Convert the image to RGB mode
        img.save(io.BytesIO(), format='JPEG', optimize=True, quality=70)

        compressed_image = io.BytesIO()
        img.save(compressed_image, format='JPEG')
        compressed_image.seek(0)

        filename = f"{int(datetime.now().timestamp()*1000)}.jpeg"
        path = os.path.join("temp", filename)

        save_path = os.path.join(PATH_STATIC, path)

        with open(save_path, 'wb') as f:
            f.write(compressed_image.read())
                    
        return path

    except Exception as e:
        return str(e)

def get_unique_filenames(folder_name):
    """ Возвращает название уникальных названий файлов и количество этого названия в папке"""
    filenames = {}
    seen = set()
    folder_path = os.path.join(PATH, folder_name)

    for _, _, files in os.walk(folder_path):
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
            with open(path) as card:
                root = etree.fromstring(card.read())
            post_data["uniqueTemplates"][post_data["selectedTemplate"]]["forms"].append(get_map_template(root))
        return jsonify(post_data)
    except Exception as e:
        return str(e), 500
    
@app.route("/static/<file>", methods = ['GET'])
def get_img(file):
    path = os.path.join(PATH_STATIC, "static", file)
    if not os.path.exists(path):
        return "", 404
    
    return send_file(path, mimetype="image/png")

@app.route("/static_map/", methods=['GET'])
def get_img_map():
    path = os.path.join(PATH_STATIC, "static")
    rtn = []
    
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            rtn.append({'name': file, 'url': f"http://{IP}/static/{file}"})

    return jsonify(rtn)

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
        except Exception as ex:
            print(ex)
            return "failed", 500

    return send_file(path, mimetype="image/svg+xml")

@app.route("/pdf/<folder>", methods=["POST"])
def pdf(folder):
    path = os.path.join(PATH, folder)
    post_data = request.get_json()
    pdf_, file_name = get_pdf(post_data, path) # filename только для того, чтобы не было случайных скачиваний одного и того же файла

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        pdf_.save()
        tmp.write(open(file_name, 'rb').read())
        os.remove(file_name)

    response = make_response()
    response.data = open(tmp.name, 'rb').read()  # содержимое ответа
    response.headers['Content-Type'] = 'application/pdf'  # тип контента
    response.headers['Content-Disposition'] = 'attachment;'  # тип скачивания
    return response

@app.route("/addTemplates/", methods=["POST"])
def add():
    name = request.form.get('name')
    files = request.files.getlist('files[]')
    for i, file in enumerate(files):
        filename = f'{name}-{i+1}.svg'
        file.save(os.path.join("templates/", filename))
    return 'Files uploaded successfully'

@app.route("/delete/<file>", methods=["GET"])
def delete(file):
    try:
        if (len(file.split('.')) == 1):
            for filename in os.listdir("templates"):
                if filename.startswith(file):
                    os.remove(os.path.join("templates", filename))
            return "Success, all files removed"
        else:
            os.remove(os.path.join(PATH_STATIC, 'static', file))
            return "Success, delete file: " + file
    except Exception as ex:
        return ex, 404
    
@app.route("/addImage/",methods=["POST"])
def add_image():
    try:
        files = request.files.getlist('images[]')
        names = request.form.getlist('names[]')
        
        for i, file in enumerate(files):
            filename = names[i]
            path = os.path.join(PATH_STATIC, "static", filename)
            file.save(path)
        return 'Images uploaded successfully'
    except Exception as ex:
        return ex, 404
    
@app.route("/updateSVG/", methods=["POST"])
def update_svg_static():
    post_data = request.get_json()
    root = etree.fromstring(post_data['data_svg'])
    try:
        for e in update_svg_template(root, None, 0, "", True):
            root.append(e)
    except Exception as ex:
        return ex, 488
    return etree.tostring(root)
