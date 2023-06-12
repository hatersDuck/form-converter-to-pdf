<template>
  <div v-if="show" class="previewWin" @click.stop="hideDialog">
    <div @click.stop class="content">
      <div v-if="dataSVG !== ''" type="image/svg+xml" :innerHTML="dataSVG"></div>
      <object v-else type="image/svg+xml" :data="path" ></object>
      <br />
      <button v-if="page < count" class="chngPage right" @click="changePage(1)">
        ⇒
      </button>
      <div v-else class="chngPage right" @click="hideDialog">↷</div>
      <button
        v-if="page >= count && page !== 1"
        class="chngPage left"
        @click="changePage(-1)"
      >
        ⇐
      </button>
      <div
        v-if="page < count && page === 1"
        class="chngPage left"
        @click="hideDialog"
      >
        ↶
      </div>
    </div>
  </div>
</template>

<script>
import {
    parse as SVGParse
} from 'svg-parser';

export default {
    props: {
        show: {
            type: Boolean,
            default: false
        },
        path: {
            type: String,
            default: "",
        },
        count: {
            type: Number,
            default: 1,
        },
        info: {
            type: Object,
        },
        imgUrls: {
            type: Array,
            default: []
        },
        dataSVG: {
            type: String
        }
    },
    data() {
        return {
            page: 1,
        }
    },
    methods: {
        hideDialog() {
            this.$emit("update:show", false);
        },
        changePage(page) {  
            const num = this.path.split("-")[1].split(".")[0];
            const newPage = parseInt(num) + page;
            this.$emit("update:path", this.path.replace(/\d/g, newPage));
            this.$emit("pageChange", this.path.replace(/\d/g, newPage))
            this.page = newPage;
        },
    },
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
}

.content {
    margin: auto;
    background-color: white;
    border-radius: 20px;
}

.chngPage {
    position: fixed;
    bottom: 3%;
    font-size: 1337%;
    color: #4d45a4;
    text-align: center;
    height: 800px;
    background-color: rgba(5, 5, 5, 0.1);
    border: 0px;
    width: 12%;
    border-radius: 10px;
}

.chngPage:hover,
.chngPage:focus {
    background-color: rgba(255, 255, 255, 0.05);
    color: #4d45a4;
}

.right {
    right: 5%;
    bottom: 10%;
    top: 10%;
}

.left {
    left: 5%;
    bottom: 10%;
    top: 10%
}
</style>
