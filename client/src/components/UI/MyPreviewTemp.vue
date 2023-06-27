<template>
  <div v-if="showPreview" class="previewWin" @click.stop="hideDialog">
    <div class="content" :style="{transform: 'scale(' + scale + ')'}">
        <div type="image/svg+xml" :innerHTML="dataSVG[page-1]" @click.stop></div>
    <br />
    </div>
    <div @click.stop>
        <button v-if="page < dataSVG.length" class="chngPage right" @click="changePage(1)">
            ⇒
        </button>
        <div v-else class="chngPage right" @click="hideDialog">↷</div>
        <button
            v-if="page <= dataSVG.length && page !== 1"
            class="chngPage left"
            @click="changePage(-1)"
        >
            ⇐
        </button>
        <div
            v-if="page < dataSVG.length && page === 1"
            class="chngPage left"
            @click="hideDialog"
        >
            ↶
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
        }
    },
    data() {
        return {
            page: 1,
        }
    },
    methods: {
        hideDialog() {
            this.$emit("hide", false);
        },
        changePage(page) {  
            this.page = this.page + page;
        },
    },
    computed: {
        scale: 
        function() {
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
    justify-content: center; /* center content horizontally */
    align-items: center; /* center content vertically */
}

.content {
    margin: auto;
    padding: auto;
    background-color: white;
    border-radius: 20px;
}

.chngPage {
    position: fixed;
    bottom: 3%;
    font-size: 3vh;
    padding: 2vh 4vh;
    border-radius: 20px;
    border: 2px solid black;
}

.right {
    right: 2%;
}

.left {
    left: 2%;
}
</style>

