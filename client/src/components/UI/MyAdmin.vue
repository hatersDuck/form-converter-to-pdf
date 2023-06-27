
<template>
    <div style="padding-top: 20px;">
        <div v-if="template">
            <MyEditableTitle v-model="name" placeholder = "Enter name template"/>

            <label for="chs" class="custom-file-upload">Add templates</label>
            <input id="chs" type="file" @change="handleFileUpload" multiple accept=".svg" />
            <div v-if = "files.length > 0">
                <div class="files-list">
                    <div class="files-list-header">Files</div>
                    <div class="files-list-body">   
                        <div v-for="(file, index) in files" :key="index" class="files-list-item">
                            <div class="files-list-item-index">{{ index + 1 }}</div>
                            <div class="files-list-item-name">{{ file.name }}</div>
                            <div class="files-list-item-buttons">
                                <button @click="moveUp(index)" :disabled="index == 0">▲</button>
                                <button @click="moveDown(index)" :disabled="index == files.length - 1">▼</button>
                            </div>
                            <div class="files-list-item-buttons">
                                <button @click="deleteFile(index)">X</button>
                            </div>

                        </div>
                    </div>
                </div>
                <button v-if="template" class="button botButt" @click="showPreviewTemplate(true)">Show preview</button>
            </div>
        </div>
        <div v-else>
            <label for="chs_imgs" class="custom-file-upload">Add static images</label>
            <input id="chs_imgs" type="file" @change="handleImgUpload" multiple accept="image/jpeg, image/png, image/gif, image/bmp, image/tiff"/> 
            <div class="files-list" v-if="imgs.length > 0">
                <div class="files-list-header">Static Images</div>
                    <div class="files-list-body">   
                        <div v-for="(file, index) in imgs" :key="index" class="files-list-item">
                            <MyEditableTitle v-model="imgs_name[index]"/>
                            <div class="files-list-item-buttons">
                                <button @click="deleteImg(index)">X</button>
                            </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div v-if = "files.length > 0 || imgs.length > 0">
            <button class="button botButt" @click="sendFiles">Submit</button>
            <p>{{ success[0] }} </p>
            <p>{{ success[1] }} </p>
        </div>
        
        <button v-if="!template" class="button botButt" @click="showPreviewStatic">Show all static files</button>
    </div>
    <div v-if="!template">
        <MyStaticImagesLib :show="showStatics" @hide_img = "showPreviewStatic"/>
    </div>
    <div v-else>
        <MyPreviewTemp :showPreview="showPreview" :dataSVG="dataSVG" @hide = "showPreviewTemplate"/>
    </div>
</template>

<script>
import MyEditableTitle from './MyEditableTitle.vue';
import MyStaticImagesLib from './MyStaticImagesLib.vue'
import MyPreviewTemp from './MyPreviewTemp.vue'
import axios from 'axios';

export default {
    props: {
        template: {
            type: Boolean,
            default: false,
        }
    },
    components: {
        MyEditableTitle,
        MyStaticImagesLib,
        MyPreviewTemp,
    },
    data() {
        return {
            files: [],
            dataSVG: [],
            imgs: [],
            imgs_name: [],
            name: "",
            success: ["",""],
            showStatics: false,
            showPreview: false,
        };
    },
    methods: {
        showPreviewStatic(hide){
            this.showStatics = hide
        },
        showPreviewTemplate(hide){
            this.showPreview = hide
        },

        handleFileUpload(event) {
            const fileList = event.target.files;
            for (let i = 0; i < fileList.length; i++) {
                const file = fileList[i];
                this.files.push(file);
                
                const reader = new FileReader();

                reader.onload = async () => {
                    const request = {
                        data_svg: reader.result,
                    };
                    const response = await axios.post(`http://95.163.233.204:5000/updateSVG/`, request, {
                        headers: {
                            "Content-Type": "application/json",
                        },
                    });
                    this.dataSVG.push(response.data);
                };

                reader.readAsText(file);
            }
        },
        handleImgUpload(event){
            const fileList = event.target.files;
            for (let i = 0; i < fileList.length; i++) {
                const file = fileList[i];
                this.imgs.push(file);
                this.imgs_name.push(file.name)
            }
        },
        deleteImg(index){
            this.imgs.splice(index, 1);
            this.imgs_name.splice(index, 1);
        },
        deleteFile(index){
            this.files.splice(index, 1);
            this.dataSVG.splice(index, 1);
        },
        moveUp(index) {
            // Обработчик перемещения файла вверх по списку
            if (index > 0) {
                const temp = this.files[index - 1];
                this.files[index - 1] = this.files[index];
                this.files[index] = temp;

                const temp_svg = this.dataSVG[index - 1]
                this.dataSVG[index - 1] = this.dataSVG[index];
                this.dataSVG[index] = temp_svg;
            }
        },
        moveDown(index) {
            // Обработчик перемещения файла вниз по списку
            if (index < this.files.length - 1) {
                const temp = this.files[index + 1];
                this.files[index + 1] = this.files[index];
                this.files[index] = temp;

                const temp_svg = this.dataSVG[index + 1]
                this.dataSVG[index + 1] = this.dataSVG[index];
                this.dataSVG[index] = temp_svg;
            }
        },
        sendFiles() {
            if (this.template) {
                const formData = new FormData();
                formData.append("name", this.name);
                for (let i = 0; i < this.files.length; i++) {
                    formData.append("files[]", this.files[i]);
                }
                axios.post('http://95.163.233.204:5000/addTemplates/', formData)
                    .then(response => {
                    this.success[0] = response.data;
                })
                    .catch(error => {
                    console.error(error);
                });
            } else {
                const imgData = new FormData();
                
                for (let i = 0; i < this.imgs.length; i++) {
                    imgData.append("images[]", this.imgs[i]);
                    imgData.append("names[]", this.imgs_name[i]);
                }
                axios.post('http://95.163.233.204:5000/addImage/', imgData)
                    .then(response => {
                    this.success[1] = response.data;
                })
                    .catch(error => {
                    console.error(error);
                });
            }
        },
    },
};
</script>

<style scoped>
input[type="file"] {
  position: absolute;
  left: -9999px;
}

.custom-file-upload {
    display: inline-block;
    padding: 10px 20px;
    background-color: white;
    color: black;
    cursor: pointer;
    border-radius: 5px;
    margin-top: 20px;
}

.custom-file-upload:hover {
    background-color: #AAA;
}

.files-list {
    border: 1px solid gray;
    margin-top: 20px;
  }

  .files-list-header {
    background-color: white;
    font-size: 20px;
    text-align: center;
    color: black;
  }

  .files-list-body {
    padding: 5px;
  }

  .files-list-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 5px;
    padding: 5px;
    border: 1px solid lightgray;
  }

  .files-list-item-index {
    font-weight: bold;
    margin-right: 5px;
  }

  .files-list-item-name {
    flex-grow: 1;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .files-list-item-buttons button {
    margin-left: 5px;
    padding: 3px 5px;
    background-color: white;
    border: 1px solid gray;
    border-radius: 3px;
    cursor: pointer;
  }

  .files-list-item-buttons button:disabled {
    opacity: 0.5;
    cursor: default;
  }
</style>