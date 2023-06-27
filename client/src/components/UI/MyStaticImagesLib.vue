<template>
    <div v-if="show" class="previewWin" @click.stop="hideDialog">
      <table class="image-table">
        <tr v-for="(image, index) in images" :key="index">
          <td class="image-cell" @click.stop>
            <img :src="image.url" :alt="image.name" class="image">
            <div class="image-info">
              <span class="image-name">{{ image.name }}</span>
              <button class="delete-button" @click="deleteImage(index)">Удалить</button>
            </div>
          </td>
        </tr>
      </table>
    </div>
  </template>

  <script>
  import axios from 'axios';
  export default {
    props: {
        show: {
            type: Boolean,
            default: false
        },
    },
    data() {
      return {
        images: []
      };
    },
    mounted(){
        this.updateImages()
    },
    methods: {
        hideDialog() {
            this.$emit("hide_img", false);
            this.updateImages()
        },
        async deleteImage(index) {
            await axios.get('http://95.163.233.204:5000/delete/' + this.images[index]['name']);
            this.images.splice(index, 1);
        },
        async updateImages(){
            const response = await axios.get('http://95.163.233.204:5000/static_map/');
            this.images = []
            for (let row of response.data){
                this.images.push(row)
            }
        }
    }
  };
  </script>
  
  <style scoped>
  .previewWin {
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.9);
    position: fixed;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .image-table {
    display: flex;
    flex-wrap: wrap;
    overflow: auto;
    max-height: 600px; /* Set the maximum height of the table */
}

.image-cell {
  flex-basis: calc(10% - 10px);
  margin-right: 10px;
  margin-bottom: 10px;
}
  .image {
    width: 200px;
    height: 200px;
    margin-bottom: 10px;
  }
  
  .image-info {
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  
  .image-name {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 10px;
  }
  
  .delete-button {
    background-color: red;
    color: white;
    font-size: 16px;
    padding: 5px 10px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  </style>