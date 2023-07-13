def text_split(rows_text, cfg) -> list:
    """ Функция возвращает лист где перенесены слова, которые не вместились в строку"""
    text = []
    def find_max_length(row):
        """Ищем количество символов, чтобы они вместились на фоновый прямоугольник"""
        width = 0
        cnt = 0
        while width < cfg['width']:
            cnt+=1
            if (cnt == len(row)):
                break
            row_text = row[:cnt]
            rus, eng = count_letters(row_text)
            eng += (len(row_text) - rus - eng)
            avg_rus = rus / cnt * cfg['average_font_russian']
            avg_eng = eng / cnt * cfg['average_font_english']
            average = avg_rus + avg_eng
            width = cnt * average * cfg['font_size']

        if cnt != len(row):
            if row[cnt] != row[cnt].upper() and row[cnt-1] != row[cnt-1].upper():
                txt = ""
                for c in row_text[cnt::-1]:
                    if (c == c.upper()):
                        break
                    txt += c
                print(txt)
                cnt -= len(txt) + 1

        return cnt

    for row_text in rows_text:
        if row_text:
            counts = [find_max_length(row_text)]
            while True:
                start = sum(counts)
                if start == len(row_text):
                    break
                counts.append(find_max_length(row_text[start:]))

            for i, cnt in enumerate(counts):
                start = sum(counts[:i])
                end = start + cnt
                if start == len(row_text):
                    break
            
                if row_text[start] != ' ':
                    row_string = row_text[start:end]
                else:
                    row_string = row_text[start + 1 : end]

                text.append(row_string)
        else:
            text.append("\t")

    return text

import re

def count_letters(string):
    russian_letters = re.findall('[а-яА-Я]', string)
    english_letters = re.findall('[a-zA-Z]', string)
    
    return len(russian_letters), len(english_letters)