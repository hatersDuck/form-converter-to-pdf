<template>
<textarea :value="modelValue" @input="updateInput" class="text-block" placeholder="Paste description"></textarea>
</template>

<script>
export default{
    props: {
        modelValue: String,
        edit: Boolean
    },
    methods: {
        updateInput(event){
            this.$emit('update:modelValue', event.target.value)
        }
    },
}
</script>

<style scoped>
.text-block {
    font-size: 18px;
    background-color: white;
    color: #4d45a4;
    width: 100%;
    height: 200px;
    padding: 0;
    white-space: pre-wrap;
    word-break: break-word;
}

</style>