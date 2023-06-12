<template>
<div>
    <slot></slot> {{ num+1 }} image
    <label :for="fileInputId" 
      :class="{'button': true, 'success': fileUploaded}" 
      :style="{'color': fileUploaded ? 'white' : 'initial', 'background-color': fileUploaded ? 'rgba(10, 60, 30, 0.5)' : ''}">
        {{ fileUploaded ? 'Photo Uploaded' : 'Select Photo' }}
    </label>
    <input :id="fileInputId" type="file" accept=".png,.jpeg,.jpg,.webp" @change="onFileChange" />
    <br>
</div>
</template>

  
  
<script>
export default {
    props: {
        index: Number,
        id: String,
        num: Number,
    },
    data() {
        return {
            fileUploaded: false,
        };
    },
    computed: {
      fileInputId() {
        return `${this.id}-file-input`;
      }
    },
    methods: {
        onFileChange(event) {
            const files = event.target.files;
            this.$emit('file-selected', files, this.index, this.num);
            this.fileUploaded = true;
        },
    },
};
</script>

<style scoped>
input {
    display: none;
}
</style>
