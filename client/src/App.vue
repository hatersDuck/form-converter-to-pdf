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

                    <div v-for="(name, index) in proper['img']['names']" :key="index">
                        <MyInputPhoto @file-selected="onFileSelected" :name="name" :index="i" :id="'my-input-file-' + i + '-'+ index" :num = "index" class="text"/>
                    </div>

                    <div v-for="(d, index) in proper['row']['count']" :key="index" class="text">
                        <MyEditableTitle v-model="proper['row']['link'][index]" :placeholder = "'Enter ' + proper['row']['names'][index]" />
                    </div>

                    <div v-for="(d, index) in proper['text']['count']" :key="index" class="text">
                        <MyEditableDescription v-model="proper['text']['link'][index]" :placeholder = "'Paste ' + proper['text']['names'][index]" />
                    </div>
                </div>
            </div>
            <button v-if="selectedTemplate"  id="submit" type="file" class="button botButt" @click="onSubmitClick">
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
        :dataSVG="dataSVG"
        @pageChange="updateSVG"
        />
    </div>
</div>
</template>

<script charset="utf-8" type="text/javascript">
import MyInputPhoto from "@/components/UI/MyInputPhoto";
import MyEditableTitle from "@/components/UI/MyEditableTitle";
import MyEditableDescription from "@/components/UI/MyEditableDescription";
import MyPreview from "@/components/UI/MyPreview";

import axios from 'axios';
import "svg2pdf.js"

export default {
    components: {
        MyInputPhoto,
        MyEditableTitle,
        MyEditableDescription,
        MyPreview
    },
    data() {
        return {
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
                        this.uniqueTemplates[this.selectedTemplate]['forms'][i]['img']['link'][index] = reader.result;
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
        async onSelectTemplate() {
            const templatesFolder = "templates";
            this.actualPath = templatesFolder + "/" + this.selectedTemplate + "-1.svg"
            const request = {
                    uniqueTemplates: this.uniqueTemplates,
                    selectedTemplate: this.selectedTemplate,
                }
            const response = await axios.post('http://127.0.0.1:8081/uniqueTemplates/' + templatesFolder, request);
            this.uniqueTemplates = response.data['uniqueTemplates']

        },
        async setUniqueTemplates() {
            const templatesFolder = "templates";
            const response = await axios.get('http://127.0.0.1:8081/uniqueFilenames/' + templatesFolder);
            for (let key in response.data){
                this.uniqueTemplates[key] = {}
                this.uniqueTemplates[key]["countList"] = response.data[key];
            }

        },
        async updateSVG(_path) {
            const request = {
                uniqueTemplates: this.uniqueTemplates,
                selectedTemplate: this.selectedTemplate,
            };
            console.log(_path)
            try {
                const response = await axios.post(`http://127.0.0.1:8081/svg/${_path}`, request, {
                    headers: {
                        "Content-Type": "application/json",
                    },
                });

                this.dataSVG = response.data;
            } catch (error) {
                console.error(error);
            }
        },      
        async onSubmitClick() {
            const templatesFolder = "templates";
            const request = {
                uniqueTemplates: this.uniqueTemplates,
                selectedTemplate: this.selectedTemplate,
            };
            const response = await axios.post('http://127.0.0.1:8081/pdf/' + templatesFolder, request, { responseType: 'blob' });

            const fileUrl = URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
            const link = document.createElement('a');
            link.href = fileUrl;
            link.download = 'ex1.pdf'; 
            link.click();
            },
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
