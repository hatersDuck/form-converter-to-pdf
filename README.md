# form-converter-to-pdf
## Структура папок

- `server` - содержит код backend написанный на фреймворке flask
- `client` - содержит frontend написанный на фреймворке vue.js
    - `src` - изменяемая папка с программным кодом vue js
    - `public` - основа проекта то, что останется при build

## Запуск

В одном терминале вводишь `make server` в другом терминале `make client`

## Код

В общем и целом, в коде всё задокументированно, далее скорее описана основная концепция и краткое объяснение основной концепцию.

Строится вся ИС на одной переменной `uniqueTemplates` и 3 взаимодействиях.

## Переменная

```
uniqueTemplates = {
	'<NameTemplate>': {
		'countList': integer,
		'forms': [
			<index>: {
				'img': {
					'names': array.string,
					'link': array.string,
				},
				'row': {
					'names': array.string,
					'link': array.string,
				},
				'text': {
					'names': array.string,
					'link': array.string,
				},
			}
		],
	},
}
```

`<NameTemplate>` - это название до знака ‘-’ в папке с шаблонами.

`'countList'` - обозначает количество листов данного шаблона в папке.

`‘forms’` - основной массив, где индекс это номер листа шаблона.

Дальше идут типы модификаций подробнее о них написано в руководстве оператора. И в коде в файле `functions.py` функция `get_map_template(path)`

## Взаимодействия

`MyInputPhoto` - это кнопка загрузки фото, у неё есть сверху подпись с названием, а так же она меняется когда загружается файл

```html
<div v-for="(name, index) in proper['img']['names']" :key="index">
	<MyInputPhoto @file-selected="onFileSelected" :name="name" :index="i" :id="'my-input-file-' + i + '-'+ index" :num = "index" class="text"/>
</div>
```

`MyEditableTitle` - это input одной строчки неограниченный по символам, он не имеет подписи сверху только placeholder.

```html
<div v-for="(name, index) in proper['row']['names']" :key="index" class="text">
	<MyEditableTitle v-model="proper['row']['link'][index]" :placeholder = "'Enter ' + name" />
</div>
```

`MyEditableDescription` - это textarea такой же как выше, только в несколько строчек и немного другой шрифт для отображения.

```html
<div v-for="(name, index) in proper['text']['names']" :key="index" class="text">
    <MyEditableDescription v-model="proper['text']['link'][index]" :placeholder = "'Paste ' + name" />
</div>
```

## Объяснения

Из кода взаимодействия уже видно, за что отвечает главная переменная это за их отображения и взаимодействия с ними, все кнопки всё остальное построено лишь на том, чтобы корректно отобразить эти взаимодействия.
Так при выборе шаблона происходит парсинг svg файла и заполнение на его основе главной переменной, как только она заполнилась vue js уже отображает всё это в html. 
Кнопка preview лишь показывает текущий результат.

Export to pdf - очевидно производит экспорт в пдф.
Я думаю код и так понятный и без дополнительных слов все комментарии в `functions.py`  написаны, которые нужны для понимания внутренних процессов.

### Задача

Есть баг когда выбираешь один из шаблонов переходишь в preview и листаешь на 2 страницу, а после переходишь в другой шаблон и там нажимаешь preview то появляется кнопка назад которая введёт в 0 шаблон и это баг, который я не смог пофиксить, удачи.

Для дополнительных вопросов пиши в тг [@fakeData](https://t.me/fakeData) или на почту okeyokeyprod@gmail.com