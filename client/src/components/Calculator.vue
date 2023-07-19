<template>
    <br>
    <iframe id="calcus-iframe-Customs" width="100%" height="300" frameborder="0" style="width:1px; min-width: 100%;" scrolling="no" src="https://calcus.ru/rastamozhka-auto?embed=1" referrerpolicy="no-referrer-when-downgrade"></iframe>
    <div style="margin-top:5px; font-size: 0.9em; color:#999">Калькулятор растаможки автомобилей предоставлен сайтом <a href="https://calcus.ru/rastamozhka-auto" target="_blank">calcus.ru</a></div>
</template>
<script>
    window.addEventListener('message', function(event) {
        if (height_Customs = event.data['height_Customs']) {
            document.getElementById('calcus-iframe-Customs').style.height = height_Customs + 'px'
        }
    })
</script>