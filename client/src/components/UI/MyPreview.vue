<template>
    <div v-if="showPreview" class="previewWin" @click.stop="hideDialog">
      <div class="scrollContainer">
        <div v-for="(svg, i) in dataSVG" :key="i">
          <div class="svgWrapper" :style="{ height: scale*800 + 'px' }">
              <div v-html="svg" class="content" :style="{ transform: 'scale(' + scale + ')' }"></div>
          </div>
        </div>
      </div>
    </div>
  </template>
 
 <script> 
 export default { 
    props: { 
        showPreview: { 
            type: Boolean, 
            default: false 
        }, 
        dataSVG: { 
            type: Array, 
            default: [] }, 
        },
    methods: { 
        hideDialog() { 
            this.$emit("hide", false); 
            }, 
        }, 
    computed: { 
        scale() { 
            const mw = 1200; 
            const mh = 800;
            const w = window.innerWidth; 
            const h = window.innerHeight; 
            const scale = Math.min((w * 0.8) / mw, (h * 0.8) / mh); 
            return scale; 
            } 
        } 
    } 
</script> 
<style scoped> 
.previewWin { 
    top: 0; 
    left: 0; 
    right: 0; 
    bottom: 0; 
    background-color: rgba(0, 0, 0, 0.6); 
    position: fixed; 
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    width: 100%;
    }
    .scrollContainer {
        display: flex;
        flex-direction: column;
        align-items: center;
        overflow: scroll;
        overflow-x: hidden;
        max-height: 100%;
    }
    .scrollContainer::-webkit-scrollbar {
        width: 10px; /* Ширина ползунка */
    }

    .scrollContainer::-webkit-scrollbar-track {
        background-color: #333; /* Цвет фона трека (фоновая область ползунка) */
    }

    .scrollContainer::-webkit-scrollbar-thumb {
        background-color: #888; /* Цвет ползунка */
    }
    .svgWrapper {
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .content {
        width: 100%;
        max-width: 100%;
        height: auto;
        object-fit: contain;
        background-color: white;
    }
</style>