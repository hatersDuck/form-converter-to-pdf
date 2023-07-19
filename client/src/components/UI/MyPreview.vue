<template>
    <div v-if="showPreview" class="previewWin" @click.stop="hideDialog">
      <div class="scrollContainer">
        <div v-for="(svg, i) in dataSVG" :key="i" @click.stop>
          <div class="svgWrapper" :style="{ height: scale * 800 + 'px' }">
            <div 
                v-html="svg" class="content" :style="{ transform: 'scale(' + scale + ')' }" 
                @click.native="editable ? handleSVGClick($event) : null">
            </div>
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
        default: []
      },
      editable: {
        type: Boolean,
        default: false
      }
    },
    data() {
      return {
        selectedSVG: null,
        panel: null,
        highlightedElement: null // Сохраняем ссылку на подсвечиваемый элемент
   };
    },
    methods: {
        hideDialog() {
            if (this.highlightedElement) {
                this.highlightedElement.style.strokeWidth = '0';
            }
            if (this.panel){
                this.panel.remove()
                this.panel = null
            }
            if (this.editable){
                const svgElements = document.querySelectorAll('.content');
                var dataSVG = []
                svgElements.forEach((svgElement) => {
                    const innerHTML = svgElement.innerHTML;
                    dataSVG.push(innerHTML)
                });
                this.$emit("replaceSVG", dataSVG)
            }
            this.$emit("hide", false);
            },
        handleSVGClick(event) {
            if (this.highlightedElement) {
                this.highlightedElement.style.strokeWidth = '0';
            }
            if (this.panel){
                this.panel.remove()
                this.panel = null
            }

            const targetElement = event.target; 
            targetElement.style.stroke = 'red'; 
            targetElement.style.strokeWidth = '2px'; 
            this.highlightedElement = targetElement; 

            const attributePanel = document.createElement('div');
            attributePanel.style.position = 'absolute';
            attributePanel.style.top = `${event.clientY}px`;
            attributePanel.style.left = `${event.clientX + 10}px`;
            attributePanel.style.backgroundColor = '#333';
            attributePanel.style.padding = '10px';
            
            const attributes = targetElement.attributes;
            if (targetElement.id == ''){
                targetElement.id = ''
            }
            for (let i = 0; i < attributes.length; i++) {
                const attributeName = attributes[i].name;
                const attributeValue = attributes[i].value;
                if (['style', 'stroke-width', 'stroke'].includes(attributeName)) {
                    continue;
                }
                const attributeRow = document.createElement('div');
                attributeRow.style.marginBottom = '10px';

                const attributeNameSpan = document.createElement('span');
                attributeNameSpan.innerText = attributeName + " : ";
                attributeNameSpan.style.fontWeight = 'bold';

                const attributeValueInput = document.createElement('input');
                attributeValueInput.value = attributeValue;
                attributeValueInput.style.marginTop = '5px';
                
                attributeValueInput.addEventListener('input', () => {
                    targetElement.setAttribute(attributeName, attributeValueInput.value);
                });

                attributeRow.appendChild(attributeNameSpan);
                attributeRow.appendChild(attributeValueInput);
                attributePanel.appendChild(attributeRow);
            }
            if (targetElement.tagName == "text") {
                const textContentInput = document.createElement('input');
                textContentInput.value = targetElement.textContent;
                textContentInput.style.marginTop = '5px';

                textContentInput.addEventListener('input', () => {
                    targetElement.textContent = textContentInput.value;
                });

                const textContentRow = document.createElement('div');
                textContentRow.style.marginBottom = '10px';
                textContentRow.appendChild(document.createTextNode('Text : '));
                textContentRow.appendChild(textContentInput);
                attributePanel.appendChild(textContentRow);
            }
            document.body.appendChild(attributePanel); 
            this.panel = attributePanel
        }
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
    },
    mounted() {}
  };
  </script>
<style scoped> 
.highlight {
  border: 5px solid yellow; 
}
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