<template>
    <input class="editTitle" :value="modelValue" @input="updateInput" type="text" >
</template>

<script>
export default {
    props: {
        modelValue: String,
        edit: Boolean
    },
    methods: {
        updateInput(event) {
            this.$emit('update:modelValue', event.target.value)
        }
    },
}
</script>

<style scoped>
.editTitle {
    font-size: 20px;
    color: #4d45a4;
    width: 100%;
    border: 0px;
    padding: 0;
}
</style>
