<!--Пофиксить кнопки, они не обновляют dataSVG-->

<template>
<div class="app">
    <div class="sections-container">
        <div class="select-input">
            <h1>Converter</h1>
            <hr>
            <h2 style="font-size: 26px;">Choose template</h2>
            <select v-model="selectedTemplate" @change="onSelectTemplate">
                <option v-for="(value, key) in uniqueTemplates" :key="key">{{key}}</option>
            </select>
            <div v-if="selectedTemplate">
                <div v-for="(proper, i) in uniqueTemplates[selectedTemplate]['forms']">
                    <div v-if = "uniqueTemplates[selectedTemplate]['countList']> 1">
                        <h3 style="font-size: 24px;"> {{ i+1 }} list</h3>
                        <hr>
                    </div>

                    <div v-for="(d, index) in proper['img']['count']" :key="index">
                        <MyInputPhoto @file-selected="onFileSelected" :index="i" :id="'my-input-file-' + i + '-'+ index" :num = "index" class="text">Add</MyInputPhoto>
                    </div>

                    <div v-for="(d, index) in proper['row']['count']" :key="index" class="text">
                        <MyEditableTitle v-model="proper['row']['link'][index]" :placeholder = "'Enter ' + proper['row']['names'][index]" />
                    </div>

                    <div v-for="(d, index) in proper['text']['count']" :key="index" class="text">
                        <MyEditableDescription v-model="proper['text']['link'][index]" :placeholder = "'Paste ' + proper['text']['names'][index]" />
                    </div>
                </div>
            </div>
            <button id="submit" type="file" class="button botButt" @click="onSubmitClick">
                Export to pdf
            </button>
            <button v-if="selectedTemplate" id="preview" type="submit" class="button eyeButt" @click="onPreviewClick">
                <i class="far fa-eye"  title="Preview"></i>
            </button>
        </div>
    </div>
    <div v-if="selectedTemplate">
    <MyPreview v-model:show="showPreview" 
        v-model:path="actualPath"
        :count="uniqueTemplates[selectedTemplate]['countList']"
        :info="uniqueTemplates[selectedTemplate]"
        :imgUrls="imageUrls"
        :dataSVG="dataSVG"
        @pageChange="updateSVG"
        />
    </div>
</div>
</template>

<script>
import MyInputPhoto from "@/components/UI/MyInputPhoto";
import MyEditableTitle from "@/components/UI/MyEditableTitle";
import MyEditableDescription from "@/components/UI/MyEditableDescription";
import MyPreview from "@/components/UI/MyPreview";

import {
    parse as SVGParse
} from 'svg-parser';
import jsPDF from "jspdf";
import 'svg2pdf.js'

export default {
    components: {
        MyInputPhoto,
        MyEditableTitle,
        MyEditableDescription,
        MyPreview
    },
    data() {
        return {
            imageUrls: [],

            uniqueTemplates: {},
            selectedTemplate: undefined,

            showPreview: false,
            actualPath: "",
            dataSVG: "",
            dataSVGdoc: {},
        };
    },
    mounted() {
        this.setUniqueTemplates();
    },
    methods: {
        onFileSelected(files, i, index) {
            try {
                const file = files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.readAsDataURL(file);
                    reader.onload = () => {
                        this.imageUrls[i][index] = reader.result;
                    };
                }
            } catch (error) {
                console.error("Error occurred while processing selected file:", error);
            }
        },
        onPreviewClick(){
            this.showPreview = true;
            this.updateSVG(this.actualPath)
        },
        onSelectTemplate() {
            this.actualPath = 'templates/' + this.selectedTemplate + '-1.svg';

            for (let i = 1; i <= this.uniqueTemplates[this.selectedTemplate]["countList"]; i++) {
                const templatePath = 'templates/' + this.selectedTemplate + '-' + i + ".svg";
                
                this.uniqueTemplates[this.selectedTemplate]["forms"] = []
                fetch(templatePath)
                    .then(response => response.text())
                    .then(svg => {
                        const svgObj = SVGParse(svg);
                        const index = i-1

                        this.uniqueTemplates[this.selectedTemplate]["forms"][index] = {}

                        this.uniqueTemplates[this.selectedTemplate]["forms"][index]["img"] = {}
                        this.uniqueTemplates[this.selectedTemplate]["forms"][index]["img"]["count"] = 0

                        this.uniqueTemplates[this.selectedTemplate]["forms"][index]["row"] = {}
                        this.uniqueTemplates[this.selectedTemplate]["forms"][index]["row"]["count"] = 0
                        this.uniqueTemplates[this.selectedTemplate]["forms"][index]["row"]["names"] = []
                        this.uniqueTemplates[this.selectedTemplate]["forms"][index]["row"]["link"] = []

                        this.uniqueTemplates[this.selectedTemplate]["forms"][index]["text"] = {}
                        this.uniqueTemplates[this.selectedTemplate]["forms"][index]["text"]["count"] = 0
                        this.uniqueTemplates[this.selectedTemplate]["forms"][index]["text"]["names"] = []
                        this.uniqueTemplates[this.selectedTemplate]["forms"][index]["text"]["link"] = []

                        for (const children of svgObj.children[0].children) {
                            const id_arr = children.properties["id"].split("-")
                            const type_ = id_arr[0]

                            switch (type_) {
                                case 'img':
                                    this.uniqueTemplates[this.selectedTemplate]["forms"][index][type_]["count"]++;
                                    break
                                case 'row': case 'text':
                                    this.uniqueTemplates[this.selectedTemplate]["forms"][index][type_]["count"]++;
                                    this.uniqueTemplates[this.selectedTemplate]["forms"][index][type_]["names"].push(id_arr[2])
                                    this.uniqueTemplates[this.selectedTemplate]["forms"][index][type_]["link"].push("")
                                    break
                            }
                        }
                        this.imageUrls[index] = new Array(this.uniqueTemplates[this.selectedTemplate]["forms"][index]["img"]["count"]).fill(null);
                    })
                    .catch(error => console.error(error));
            }
            
        },
        setUniqueTemplates() {
            const templatesFolder = "templates";

            fetch(templatesFolder)
                .then((response) => response.text())
                .then((html) => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, "text/html");
                    const files = Array.from(doc.querySelectorAll("a"))
                        .map((link) => link.getAttribute("href"))
                        .filter((file) => file !== "/" && file !== templatesFolder)
                        .map((file) => file.substring(file.lastIndexOf("/") + 1))
                        .map((file) => file.split("-")[0]);

                    const uniqueFiles = [...new Set(files)];

                    for (let i = 0; i < uniqueFiles.length; i++) {
                        let key = uniqueFiles[i];
                        let value = 0;

                        for (let j = 0; j < files.length; j++) {
                            if (files[j] === key) {
                                value++;
                            }
                        }

                        this.uniqueTemplates[key] = {};
                        this.uniqueTemplates[key]["countList"] = value;
                    }
                });
        },
        updateSVG(_path) {
            console.log(_path);
            return fetch(_path)
                .then(response => response.text())
                .then(svg => {
                const svgObj = SVGParse(svg);
                const svgNS = "http://www.w3.org/2000/svg";
                const parser = new DOMParser();
                const svgDoc = parser.parseFromString(svg, "image/svg+xml");
                const serializer = new XMLSerializer();
                const svgElement = svgDoc.documentElement;
                const index = parseInt(_path[_path.length-5]) - 1
                console.log(index)
                console.log("SVGOBJ: " + _path)
                console.log(svgObj)

                for (const children of svgObj.children[0].children) {
                    const row = children.properties
                    const id_arr = row["id"].split("-")
                    const type_ = id_arr[0]

                    const element = svgElement.querySelector(`[id^="${row['id']}"]`);

                    switch (type_) {
                    case 'img':
                        const num = parseInt(id_arr[1]) - 1
                        const url = this.imageUrls[index][num]
                        if(url){
                        const newImage = document.createElementNS(svgNS, "image");

                        newImage.setAttribute("x", row["x"])
                        newImage.setAttribute("y", row["y"])
                        newImage.setAttribute("width", row["width"])
                        newImage.setAttribute("height", row["height"])
                        newImage.setAttribute("preserveAspectRatio", "none")
                        newImage.setAttribute("href", url)
                        element.setAttribute("width", "0")
                        element.setAttribute("height", "0")

                        svgElement.appendChild(newImage);
                        }
                        break
                    case 'row':
                        const numeral = parseInt(id_arr[1]) - 1
                        element.textContent = this.uniqueTemplates[this.selectedTemplate]["forms"][index]['row']['link'][numeral]
                        break
                    case 'text':
                        const numeric = parseInt(id_arr[1]) - 1
                        const newTextNode = document.createElementNS(svgNS, "text");

                        const rowsTexts = this.uniqueTemplates[this.selectedTemplate]["forms"][index]['text']['link'][numeric].split('\n');
                        let dy = "0"
                        for (const rowText of rowsTexts) {
                        const newSpan = document.createElementNS(svgNS, "tspan");
                        newSpan.setAttribute('x', row['x'])
                        newSpan.setAttribute('dy', dy)
                        newSpan.textContent = rowText;

                        element.appendChild(newSpan);
                        dy = row['font-size']
                        }

                        break
                    case 'static':
                        const newImage = document.createElementNS(svgNS, "image");

                        newImage.setAttribute("x", row["x"])
                        newImage.setAttribute("y", row["y"])
                        newImage.setAttribute("width", row["width"])
                        newImage.setAttribute("height", row["height"])
                        newImage.setAttribute("preserveAspectRatio", "none")
                        newImage.setAttribute("href", 'static/' + id_arr[1])

                        element.setAttribute("width", "0")
                        element.setAttribute("height", "0")

                        svgElement.appendChild(newImage);
                        break
                    }
                }
                this.dataSVG = serializer.serializeToString(svgDoc);
                this.dataSVGdoc = svgDoc
                return this.dataSVGdoc
                })
                .catch(error => console.error(error));
            },
            async onSubmitClick() {
                const pdf = new jsPDF("l", "pt", "A4", );
                let promises = [];
                for (let i = 1; i <= this.uniqueTemplates[this.selectedTemplate]["countList"]; i++) {
                    const templatePath = 'templates/' + this.selectedTemplate + '-' + i + ".svg";
                    const promise = this.updateSVG(templatePath);
                    promises.push(promise);
                }
                Promise.all(promises).then(async dataSVGS => {
                    for (let i = 0; i < dataSVGS.length; i++) {
                        console.log("NEW DATA; ");
                        const width = pdf.internal.pageSize.width;
                        const height = pdf.internal.pageSize.height;
                        await pdf.svg(dataSVGS[i].documentElement, {"width": width, "height": height});
                        if (i !== dataSVGS.length - 1) {
                            pdf.addPage();
                        }
                    }

                    pdf.save('ex.pdf');
                });
                }
    }
}
</script>

<style>
body {
    margin: 0;
    padding: 0;
    color: #eee;
    background-color: #222;
}
.text {
    padding-top: 20px; 
    font-size: 22px;
}
h1 {
    margin-bottom: 10px;
}

.app {
    background-color: #333;
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    overflow: auto;
    display: flex;
}

.sections-container {
    width: 250px;
    height: 250px;
    position: absolute;
    top: 20%;
    left: 50%;
    margin: -125px -250px 0 -125px;
}

.select-input {
    position: relative;
    text-align: center;
}

.button {
    display: inline-block;
    padding: 10px;
    font-size: 16px;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    border: 1px solid #000;
    color: black;
    background-color: transparent;
    cursor: pointer;
    border-radius: 10px;
    background-color: white;
    margin-bottom: 20px;

}

.button:hover,
.button:focus {
    border-color: white;
    color: #4d45a4;
}

.botButt {
    padding: 20px;
    margin-top: 40px;
}

select {
    display: block;
    width: 100%;
    height: 40px;
    padding: 10px;
    border: none;
    background-color: #f7f7f7;
    color: #333;
    font-size: 16px;
    font-weight: 400;
    line-height: 1.4;
    border-radius: 5px;
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
    cursor: pointer;
}

select:focus,
select:hover {
    outline: none;
    box-shadow: 0 0 0 2px #4d45a4;
}

select option {
    font-weight: normal;
    text-align: center;
}
.eyeButt {
    background-color: #333;
    border: 0px;
    margin-left: 20px;
    color: white;
    }
</style>
