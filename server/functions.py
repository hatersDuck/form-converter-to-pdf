from lxml import etree
import os
import svglib.svglib as svglib
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.graphics import renderPDF

def all_types():
    return ['img', 'row', 'text']

def check_type(type_):
    return type_ in all_types()

def check_id(children):
    return children.attrib.get('id', False)

def get_map_template(path):
    with open(path) as card:
        root = etree.fromstring(card.read())
    rt = {}
    for type_ in all_types():
        rt[type_] = {
            "count": 0,
            "names": [],
            "link": [],
        }

    for children in root:
        if check_id(children):
            id = children.attrib['id'].split('-')
        else:
            continue
        type_ = id[0]

        if check_type(type_):
            rt[type_]["count"] += 1
            rt[type_]["names"].append(id[-1])
            rt[type_]["link"].append("")

    return rt

def update_svg_template(root, post_data, index, path_img = ""):
    elements = []
    for children in root:
        if check_id(children):
            row = children.attrib
            id_arr = row["id"].split("-")
        else:
            continue
        if (len(id_arr) <= 1):
            continue

        type_ = id_arr[0]
        element = root.xpath(f"//*[starts-with(@id, '{row['id']}')]")[0]
        
        if check_type(type_):
            form = post_data["uniqueTemplates"][post_data["selectedTemplate"]]["forms"][index]
            num = int(id_arr[1]) - 1
        else:
            if type_ == "static":
                static_path = os.path.join(path_img, 'static', id_arr[1])
                new_image = etree.Element("image", 
                                            x=row["x"], y=row["y"], width=row["width"], 
                                            height=row["height"], preserveAspectRatio="none", href=static_path)
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
                element.set("width", "0")
                element.set("height", "0")
                elements.append(new_image)

        elif type_ == "row":
            text = form['row']['link'][num]
            element.text = text

        elif type_ == "text":
            rows_texts = form['text']['link'][num].split('\n')
            
            dy = "0"
            for row_text in rows_texts:
                new_span = etree.Element("tspan", x=row['x'], dy=dy)
                new_span.text = row_text if row_text else "\t"
                element.append(new_span)
                dy = row['font-size']

    return elements

def get_pdf(post_data, folder):
    pdf = canvas.Canvas('ex1.pdf', pagesize=landscape(A4))
    x_offset = 0
    y_offset = 0
    width, height = landscape(A4)

    for i in  range(1, 
                    post_data["uniqueTemplates"][post_data["selectedTemplate"]]['countList']+1):
        template_path = f'{post_data["selectedTemplate"]}-{i}.svg'
        path = os.path.join(folder, template_path)

        with open(path) as card:
            root = etree.fromstring(card.read())
        for e in update_svg_template(root, post_data, i-1, os.path.join("/".join(path.split("/")[:-2]))):
            root.append(e)
        
        svg_data = etree.tostring(root)

        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.svg') as tmp:
            tmp.write(svg_data)
            tmp.flush()
            drawing = svglib.svg2rlg(tmp.name)

        drawing_scale_x = width / drawing.width
        drawing_scale_y = height / drawing.height
        drawing.scale(drawing_scale_x, drawing_scale_y)

        renderPDF.draw(drawing, pdf, x_offset, y_offset)

        if i != post_data["uniqueTemplates"][post_data["selectedTemplate"]]['countList']:
            pdf.showPage()

    return pdf