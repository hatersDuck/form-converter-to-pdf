<template>
<div class="app">
    <div class="sections-container">
        <div class="select-input">
            <h1>{{ msg['title'] }}</h1>
            <hr>
            <select v-model="selectedLanguage" style="background-color: #333; font-size: 16px; color: white;" @change="fetchLanguage">
                <option value="en">English 🇬🇧</option>
                <option value="ch">中国 🇨🇳</option>
            </select>
            <h2 style="font-size: 26px;">{{ msg['choose'] }}</h2>
            <select v-model="selectedTemplate" @change="onSelectTemplate">
                <option v-for="(value, key) in uniqueTemplates" :key="key">{{key}}</option>
                <option v-if="isAdmin" disabled value=""></option>
                <option v-if="isAdmin" value="add_template" style="background-color: grey; color:white;">Add Template</option>
                <option v-if="isAdmin" value="add_image" style="background-color: grey; color:white;">Add Images</option>
            </select>
            <div v-if="selectedTemplate && selectedTemplate != 'add_template' && selectedTemplate != 'add_image'">
                <div v-if="isAdmin">
                    <button id="submit" type="file" style="background-color: red; font-size: 10px;" @click="deleteTemplate">
                        <div v-if="deletes">YOU SURE?</div><div v-else>DELETE TEMPLATE</div>
                    </button>
                </div>
                <div v-for="(proper, i) in uniqueTemplates[selectedTemplate]['forms']">
                    <div v-if = "uniqueTemplates[selectedTemplate]['countList']> 1">
                        <h3 style="font-size: 24px;"> {{ i+1 }} list</h3>
                        <hr>
                    </div>

                    <div v-for="(name, index) in proper['img']['names']" :key="index">
                        <MyInputPhoto @file-selected="onFileSelected" :msg="msg" :name="name" :index="i" :id="'my-input-file-' + i + '-'+ index" :num = "index" class="text"/>
                    </div>

                    <div v-for="(name, index) in proper['row']['names']" :key="index" class="text">
                        <MyEditableTitle v-model="proper['row']['link'][index]" :placeholder = "msg['enter'] + ' ' + name" />
                    </div>

                    <div v-for="(name, index) in proper['text']['names']" :key="index" class="text">
                        <MyEditableDescription v-model="proper['text']['link'][index]" :placeholder = "msg['paste'] + ' ' + name" />
                    </div>
                </div>
                <hr>
                <button class="button" @click="onPreviewClick(true)">
                    {{ msg['preview'] }}
                </button>
                <br>
                <button id="submit" type="file" class="button botButt" @click="onSubmitClick">
                    {{msg['export']}}
                </button>
            </div>
            <div v-if="selectedTemplate == 'add_template'">
                <MyAdmin :template="true"/>
            </div>
            <div v-if="selectedTemplate == 'add_image'">
                <MyAdmin/>
            </div>
        </div>
    </div>
    <MyPreview :showPreview="showPreview" :dataSVG="dataSVG" :page="page" @hide="onPreviewClick" @changePage="changePage"/>
</div>
</template>

<script charset="utf-8" type="text/javascript">
import MyInputPhoto from "@/components/UI/MyInputPhoto";
import MyEditableTitle from "@/components/UI/MyEditableTitle";
import MyEditableDescription from "@/components/UI/MyEditableDescription";
import MyPreview from "@/components/UI/MyPreview";
import MyAdmin from "@/components/UI/MyAdmin";

import axios from 'axios';

import messages from "@/messages.json"

export default {
    components: {
        MyInputPhoto,
        MyEditableTitle,
        MyEditableDescription,
        MyPreview,
        MyAdmin,
    },
    data() {
        return {
            selectedLanguage: "en",
            msg: {},
            uniqueTemplates: {},
            selectedTemplate: undefined,

            showPreview: false,
            actualPath: "",
            dataSVG: [],
            dataSVGdoc: {},
            
            deletes: false,
            files: [],
        };
    },
    created() {
        this.fetchLanguage();
    },
    mounted() {
        this.setUniqueTemplates();  
    },
    computed: {
        isAdmin() {
            const params = new URLSearchParams(window.location.search)
            return params.get('admin') === '1'
        }
    },
    methods: {
        fetchLanguage() {
            this.msg = messages;
            this.msg = this.msg[this.selectedLanguage]
        },

        onFileSelected(files, i, index) {
        try {
            const file = files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = async () => {
                try {
                    const formData = new FormData();
                    formData.append('image', file);

                    const url = 'http://95.163.233.204:5000/compress';

                    const response = await axios.post(url, formData);
                    const compressedImage = response.data;

                    this.uniqueTemplates[this.selectedTemplate]['forms'][i]['img']['link'][index] = compressedImage;
                    this.updateSVG(i);
                } catch (error) {
                    console.error('Error occurred while processing selected file:', error);
                    }
                };
                reader.readAsDataURL(file);
            }
        } catch (error) {
            console.error('Error occurred while processing selected file:', error);
        }
        },

        async deleteTemplate(){
            if (!this.deletes){
                this.deletes = true
            } else {
                await axios.get('http://95.163.233.204:5000/delete/' + this.selectedTemplate);
                this.selectedTemplate = ""
                location.reload();
            }
        },
        
        onPreviewClick(hide){
            this.showPreview = hide;
            if (hide) {
                for (let i = 0; i < this.dataSVG.length; i++){
                    this.updateSVG(i)
                }
            }
                
        },

        changePage(page) {
            this.page = this.page + page;
            this.updateSVG(this.page-1)
        },
        
        async onSelectTemplate() {
            if (this.selectedTemplate !== "add_template" && this.selectedTemplate !== "add_image") {
                const templatesFolder = "templates";

                const request = {
                        uniqueTemplates: this.uniqueTemplates,
                        selectedTemplate: this.selectedTemplate,
                    }
                const response_templates = await axios.post('http://95.163.233.204:5000/uniqueTemplates/' + templatesFolder, request);
                this.uniqueTemplates = response_templates.data['uniqueTemplates']

                const countList = this.uniqueTemplates[this.selectedTemplate]['countList']
                this.dataSVG.length = countList
                for (let i = 0; i < countList; i++){ this.updateSVG(i) }
            }
        },
        async setUniqueTemplates() {
            const templatesFolder = "templates";
            const response = await axios.get('http://95.163.233.204:5000/uniqueFilenames/' + templatesFolder);
            for (let key in response.data){
                this.uniqueTemplates[key] = {}
                this.uniqueTemplates[key]["countList"] = response.data[key];
                const request = {
                        uniqueTemplates: this.uniqueTemplates,
                        selectedTemplate: key,
                    }
                const response_templates = await axios.post('http://95.163.233.204:5000/uniqueTemplates/' + templatesFolder, request);
                this.uniqueTemplates = response_templates.data['uniqueTemplates']
            }

        },
        async updateSVG(index) {
            console.log("update", index)
            const templatesFolder = "templates";
            const request = {
                uniqueTemplates: this.uniqueTemplates,
                selectedTemplate: this.selectedTemplate,
            };
            try {
                const path = `${templatesFolder}/${this.selectedTemplate}-${index+1}.svg`;
                const response = await axios.post(`http://95.163.233.204:5000/svg/${path}`, request, {
                    headers: {
                        "Content-Type": "application/json",
                    },
                });
                this.dataSVG[index] = response.data;
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

            const loadingContainer = document.createElement('div');
            loadingContainer.classList.add('loading-container');

            const loadingOverlay = document.createElement('div');
            loadingOverlay.classList.add('loading-overlay');
            loadingOverlay.addEventListener('click', function(event) {
                    event.stopPropagation();
                });

            const loadingElement = document.createElement('div');
            loadingElement.classList.add('loading');

            const textElement = document.createElement('p');
            textElement.classList.add('progress-text');

            loadingContainer.appendChild(loadingElement);
            loadingContainer.appendChild(textElement);

            document.body.appendChild(loadingOverlay);
            document.body.appendChild(loadingContainer);

            try {
                const uploadStartTime = Date.now();
                const response = await axios.post('http://95.163.233.204:5000/pdf/' + templatesFolder, request, {
                    responseType: 'blob',
                    onUploadProgress: (progressEvent) => {
                        const { loaded, total } = progressEvent;

                        const downloaded = loaded / 1024 / 1024;
                        const remaining = total  / 1024 / 1024;
                        const elapsedTime = (Date.now() - uploadStartTime) / 1000;
                        const speed = loaded / elapsedTime / 1024;

                        textElement.textContent = `${downloaded.toFixed(2)}/${remaining.toFixed(2)} Mb| ${speed.toFixed(2)} KB/s`;
                    },
                });

                const fileUrl = URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
                const link = document.createElement('a');
                link.href = fileUrl;
                link.download = this.selectedTemplate + '.pdf';
                link.click();
            } catch (error) {
                console.error(error);
            } finally {
                setTimeout(() => {
                    document.body.removeChild(loadingContainer);
                    document.body.removeChild(loadingOverlay);

                    this.setUniqueTemplates();
                }, 500);
            }
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

body {
    background-color: #333;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}
.loading-container {
    position: relative;
}

.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 1;
    pointer-events: auto;
}

.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    z-index: 2;
}

.loading {
    width: 50px;
    height: 50px;
    border-radius: 100%;
    border: 5px solid #f3f3f3;
    border-top: 5px solid #3498db;
    animation: spin 1s linear infinite;
}

.progress-text {
    position: relative;
    top: 50%;
    transform: translateY(-50%);
    display: block;
    color: greenyellow;
    font-size: 20px;
    text-align: center;
    margin-top: 10px;
    font-weight: bold;
    text-shadow: 1px 1px 1px #000;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}
</style>
