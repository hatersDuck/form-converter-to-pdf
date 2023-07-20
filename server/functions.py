from lxml import etree
import os

import svglib.svglib as svglib
from svglib.svglib import register_font
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from datetime import datetime
import tempfile
from const import PATH, PATH_STATIC, FONT, NS
from algorithms import text_split, count_letters

# path_font = os.path.join(PATH_STATIC, "fonts", f"{FONT}.ttf")
# pdfmetrics.registerFont(TTFont(FONT, path_font))
# print(register_font(FONT, path_font))

def all_types():
    """ Возвращает список доступных типов для модификации """
    return ['img', 'row', 'text']

def check_type(type_):
    """ Проверяет тип на наличие в списке доступных типов для модификации"""
    return type_ in all_types()

def check_id(children):
    """ Проверяет наличие атрибута id у переданного дочернего элемента."""
    id = children.attrib.get('id', False)
    if id:
        if len(id.split('-')) == 1:
            id = False
    return id

def check_g(root):
    """ Проверяет существование группы элементов в корне. """
    return root[0].tag[-1] == 'g' # Сделано лишь для того, что некоторые сайты их используют, а человек может забыть

def get_map_template(root) -> dict:
    """ Возвращает список для отображение form, а так же их связку и их input """
    rt = {}
    for type_ in all_types():
        rt[type_] = {
            "names": [],    # Имена для отображения пользователю
            "link": [],     # Значение с input
        }

    while check_g(root):
        root = root[0]
    
    for children in root:
        if check_id(children):
            id = children.attrib['id'].split('-') # Парсим id
        else:
            continue # Если нет id то дальнейшии операции бесмысслены
        type_ = id[0] # Забираем тип

        if check_type(type_): 
            # Заполняем список
            rt[type_]["names"].append(id[-1])
            rt[type_]["link"].append("")

    return rt

def text_element(root, element):
    pass

def update_svg_template(root, post_data, index, path_img = "", only_static=False) -> list:
    """ Возвращает SVG-элементы шаблона на основе данных, переданных в post_data. """
    # Тут происходит вся магия
    elements = []
    images_path = []
    for children in [*root.findall(NS+"text"), *root.findall(NS+"rect")]:
        if check_id(children):
            row = children.attrib # Если id есть парсим все атрибуты
            id_arr = row["id"].split("-") # Парсим id
        else:
            if children.tag.replace(NS, '') == 'text':
                children.set('font-family', FONT)
            continue
        if (len(id_arr) <= 1): # Если id заполнен неверно, то скипаем
            continue

        type_ = id_arr[0]
        # Берём элемент вообще можно взять другим способом, но мне что первое в голову пришло, то я и оставлю, так ещё и выглядит грозно ))
        element = root.xpath(f"//*[starts-with(@id, '{row['id']}')]")[0]

        if check_type(type_) and not(only_static):
            form = post_data["uniqueTemplates"][post_data["selectedTemplate"]]["forms"][index]
            num = int(id_arr[1]) - 1 # type-num-name
        else:
            if type_ == "static":   # Единственный тип как бы модифицированный, но он просто берёт путь
                static_path = os.path.join('static', id_arr[1]) # Путь до картинки
                if (path_img):
                    for img in root.findall(NS+"image"):
                        if img.attrib['href'] ==  static_path:
                            img.set('href', os.path.join(path_img, static_path))
                else:
                    new_image = etree.Element("image", 
                                                x=row["x"], y=row["y"], width=row["width"], 
                                                height=row["height"], preserveAspectRatio="none", href=static_path)
                    element.set("width", "0")
                    element.set("height", "0")
                    elements.append(new_image)
            else:
                continue

        if not(only_static):
            if type_ == "img":
                url = os.path.join(path_img, form['img']['link'][num])
                if url != path_img:
                    new_image = etree.Element("image", 
                                                x=row["x"], y=row["y"], width=row["width"], 
                                                height=row["height"], preserveAspectRatio="none", href=url)
                    # Обнуляем длину-ширину, чтобы небыло рамки от фигуры
                    element.set("width", "0")
                    element.set("height", "0")

                    images_path.append(form['img']['link'][num])
                    elements.append(new_image)

            elif type_ == "row":
                text = form['row']['link'][num]
                element.text = text
                element.attrib['font-family'] = FONT 

            elif type_ == "text":
                element.attrib['font-family'] = FONT
                rows_text = form['text']['link'][num].split('\n')
                text_x = float(element.get("x", 0))
                text_y = float(element.get("y", 0))
                
                # Поиск ближайшего прямоугольника
                nearest_rect = None
                min_distance = float('inf')

                x = 0
                for rect in root.findall(NS+"rect"):
                    rect_x = float(rect.get("x", 0))
                    rect_y = float(rect.get("y", 0))

                    # Юзал самую дефолтную формулу из векторной алгебры
                    distance = ((text_x - rect_x) ** 2 + (text_y - rect_y) ** 2) ** 0.5

                    if distance < min_distance:
                        min_distance = distance
                        x = rect_x
                        nearest_rect = rect

                if nearest_rect is not None:
                    cfg = {
                        "font_size": int(row.get("font-size", 1).replace("px", "")),
                        "width": float(nearest_rect.get("width").replace("px", "")) + (text_x- x),
                        "average_font_english": 0.62, # Это для DejaVu Sans,
                        "average_font_russian": 0.75,
                    }

                dy = "0" # Изначальный y обычно делают отступом сверху в самом редакторе поэтому зануляем

                for row_text in text_split(rows_text, cfg):
                    new_span = etree.Element("tspan", x=row['x'], dy=dy) 
                    new_span.text = row_text
                    
                    element.append(new_span)
                    dy = row['font-size'] # делаем отступ в размер шрифта можно прибавить для красоты какую нибудь константу
    
    if (path_img):
        return elements, images_path
    
    return elements

def get_pdf(post_data, folder):
    """ Возвращает pdf файл(canvas), и название файла """
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S;%s")
    file_name = post_data['selectedTemplate'] + current_time + ".pdf"

    pdf = canvas.Canvas(file_name, pagesize=landscape(A4))
    x_offset = 0
    y_offset = 0
    width, height = landscape(A4)
    images = []

    for i in  range(1, 
                    post_data["uniqueTemplates"][post_data["selectedTemplate"]]['countList']+1): # проходимся по всем листам
        
        template_path = f'{post_data["selectedTemplate"]}-{i}.svg' 
        path = os.path.join(folder, template_path)

        with open(path) as card:
            root = etree.fromstring(card.read())
        # Обновляем svg и так как мы в папке сервер, и даём полный путь до статики
        elements, img = update_svg_template(root, post_data, i-1, PATH_STATIC)
        for e in elements: 
            root.append(e)
        
        images.append(img)
        svg_data = etree.tostring(root)
        
        with tempfile.NamedTemporaryFile(suffix='.svg') as tmp:
            tmp.write(svg_data)
            tmp.flush()
            drawing = svglib.svg2rlg(tmp.name)

        # Подводим размеры к альбомному формату
        drawing_scale_x = width / drawing.width 
        drawing_scale_y = height / drawing.height
        
        drawing.scale(drawing_scale_x, drawing_scale_y)

        renderPDF.draw(drawing, pdf, x_offset, y_offset)
        # Если это не последняя страница добавляем пустую страницу
        if i != post_data["uniqueTemplates"][post_data["selectedTemplate"]]['countList']: 
            pdf.showPage()

    delete_temp(images)
    return pdf, file_name

def delete_temp(images):
    for paths in images:
        for path in paths:
            os.remove(os.path.join(PATH_STATIC, path))

def validate(dataSVG) -> bool:
    """ Правильно ли праставлены все теги или нет """
    root = etree.fromstring(dataSVG)
    elements = []
    images_path = []
    for children in [*root.findall(NS+"text"), *root.findall(NS+"rect")]:
        if check_id(children):
            row = children.attrib 
            id_arr = row["id"].split("-") 
        else:
            if children.tag.replace(NS, '') == 'text':
                children.set('font-family', FONT)
            continue
        if (len(id_arr) <= 1): 
            continue

        type_ = id_arr[0]
        element = root.xpath(f"//*[starts-with(@id, '{row['id']}')]")[0]

        if check_type(type_):
            num = int(id_arr[1]) - 1 
        else:
            if type_ == "static":   
                new_image = etree.Element("image", 
                                            x=row["x"], y=row["y"], width=row["width"], 
                                            height=row["height"], preserveAspectRatio="none", href="")
                element.set("width", "0") 
                element.set("height", "0")

                elements.append(new_image)
            else:
                continue
        if type_ == "img":
            new_image = etree.Element("image", 
                                        x=row["x"], y=row["y"], width=row["width"], 
                                        height=row["height"], preserveAspectRatio="none", href="")
            element.set("width", "0")
            element.set("height", "0")
            elements.append(new_image)

        elif type_ == "row":
            element.attrib['font-family'] = FONT 

        elif type_ == "text":
            element.attrib['font-family'] = FONT
            text_x = float(element.get("x", 0))
            text_y = float(element.get("y", 0))
    
    return elements