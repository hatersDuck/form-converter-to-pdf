from lxml import etree
import os
import svglib.svglib as svglib
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.graphics import renderPDF
from datetime import datetime

def all_types():
    """ Возвращает список доступных типов для модификации """
    return ['img', 'row', 'text']

def check_type(type_):
    """ Проверяет тип на наличие в списке доступных типов для модификации"""
    return type_ in all_types()

def check_id(children):
    """ Проверяет наличие атрибута id у переданного дочернего элемента."""
    return children.attrib.get('id', False)

def check_g(root):
    """ Проверяет существование группы элементов в корне. """
    return root[0].tag[-1] == 'g' # Сделано лишь для того, что некоторые сайты их используют, а человек может забыть

def get_map_template(path) -> dict:
    """ Возвращает список для отображение form, а так же их связку и их input """
    with open(path) as card:
        root = etree.fromstring(card.read())
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

def update_svg_template(root, post_data, index, path_img = "") -> list:
    """ Возвращает SVG-элементы шаблона на основе данных, переданных в post_data. """
    # Тут происходит вся магия
    elements = []
    for children in root:
        if check_id(children):
            row = children.attrib # Если id есть парсим все атрибуты
            id_arr = row["id"].split("-") # Парсим id
        else:
            continue
        if (len(id_arr) <= 1): # Если id заполнен неверно, то скипаем
            continue

        type_ = id_arr[0] 
        element = root.xpath(f"//*[starts-with(@id, '{row['id']}')]")[0] # берём элемент вообще можно взять другим способом, но мне что первое в голову пришло, то я и оставлю, так ещё и выглядит грозно ))
        
        if check_type(type_):
            form = post_data["uniqueTemplates"][post_data["selectedTemplate"]]["forms"][index] # просто сокрашение записи
            num = int(id_arr[1]) - 1 # type-num-name - Вообще можно придумать систему где num будет не нужен, но что-то в падлу
        else:
            if type_ == "static":   # Единственный тип как, бы модифицированный, но он просто берёт путь
                static_path = os.path.join(path_img, 'static', id_arr[1]) # Путь до картинки
                new_image = etree.Element("image", 
                                            x=row["x"], y=row["y"], width=row["width"], 
                                            height=row["height"], preserveAspectRatio="none", href=static_path)
                # Обнуляем длину-ширину, чтобы небыло рамки от фигуры
                element.set("width", "0") 
                element.set("height", "0")

                elements.append(new_image)
            else:
                continue
         
        if type_ == "img":
            url = form['img']['link'][num]
            if url:
                new_image = etree.Element("image", 
                                            x=row["x"], y=row["y"], width=row["width"], 
                                            height=row["height"], preserveAspectRatio="none", href=url)
                # Обнуляем длину-ширину, чтобы небыло рамки от фигуры
                element.set("width", "0")
                element.set("height", "0")

                elements.append(new_image)

        elif type_ == "row":
            text = form['row']['link'][num]
            element.text = text

        elif type_ == "text":
            rows_texts = form['text']['link'][num].split('\n')
            
            dy = "0" # Изначальный y обычно делают отступом сверху в самом редакторе поэтому зануляем
            for row_text in rows_texts:
                new_span = etree.Element("tspan", x=row['x'], dy=dy) 
                new_span.text = row_text if row_text else "\t" # тернарка добавлена ведь svg не хочет применять пустую строку
                
                element.append(new_span)
                dy = row['font-size'] # делаем отступ в размер шрифта можно прибавить для красоты какую нибудь константу

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

    for i in  range(1, 
                    post_data["uniqueTemplates"][post_data["selectedTemplate"]]['countList']+1): # проходимся по всем листам
        
        template_path = f'{post_data["selectedTemplate"]}-{i}.svg' 
        path = os.path.join(folder, template_path)

        with open(path) as card:
            root = etree.fromstring(card.read())
        # Обновляем svg и так как мы в папке сервер, то картинки находятся в другом месте
        for e in update_svg_template(root, post_data, i-1, os.path.join("/".join(path.split("/")[:-2]))): 
            root.append(e)
        
        svg_data = etree.tostring(root)

        import tempfile
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

    return pdf, file_name

