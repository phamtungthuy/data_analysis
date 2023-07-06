from bs4 import BeautifulSoup
import json
import glob
import os
import re
from unidecode import unidecode

final_data = []
html_files = glob.glob("./data/*.html")
count = 0
for i in range(1, 2000):
    file_path = f'./data/page{i}.html'
    count += 1
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    value = soup.select_one(".content1 div:first-child b:nth-of-type(1)")
    if value is not None: value = value.text
    have_articles = True
    general_title = ''
    arrays = []
    def int_to_roman(num):
    # Mảng chứa các giá trị và ký hiệu của số La Mã
        roman_map = [
            (1000, 'M'),
            (900, 'CM'),
            (500, 'D'),
            (400, 'CD'),
            (100, 'C'),
            (90, 'XC'),
            (50, 'L'),
            (40, 'XL'),
            (10, 'X'),
            (9, 'IX'),
            (5, 'V'),
            (4, 'IV'),
            (1, 'I')
        ]

        roman_num = ''
        for value, symbol in roman_map:
            while num >= value:
                roman_num += symbol
                num -= value

        return roman_num

    def find_first_position(start, end, target):
        for i in range(start, end + 1):
            if arrays[i].find(target) == 0:
                return i
        return -1

    def check_have_articles(start, end):
        for i in range(start, end + 1):
            if arrays[i].find('Điều') == 0:
                return True
        return False


    def handle_get_articles_and_chapters(start, end, data):
        current_article_id = 0
        current_chapter_id = 0
        start_position = -1
        structure = ["Chương",  "I.", "Điều", "1.", 'Khoản thứ nhất', 'Điều thứ nhất', 'Khoản I', '1-']
        for i in range(len(structure)):
            if start_position != -1: break
            if i >= 2: current_chapter_id = -1
            start_position = find_first_position(start, end, structure[i])
        if start_position != -1:
            current_article_title = ""
            content = []
            can_add_article = True
            for i in range(start_position, end +1):
                if arrays[i] == '':
                    break
                if current_chapter_id != -1 and (arrays[i].find('Chương') == 0 or arrays[i].find(int_to_roman(current_chapter_id + 1)) == 0):
                    if content != [] and can_add_article:
                        data['articles'].append({
                            "article_id": str(current_article_id) if current_chapter_id == -1 else f"{str(current_chapter_id)}.{str(current_article_id)}",
                            "title": current_article_title,
                            "text": '\n'.join(content)
                        })
                    content = []
                    can_add_article = False
                    current_chapter_id += 1
                    if not have_articles: current_article_id = 0
                    if arrays[i].find('Chương') == 0:
                        data['chapters'].append({
                            "chapter_id": str(current_chapter_id),
                            "title": arrays[i + 1]
                        })
                    else:
                        data['chapters'].append({
                            "chapter_id": str(current_chapter_id),
                            "title":  ' '.join(arrays[i].split(' ')[1:])
                        })
                elif arrays[i].find('Khoản thứ') == 0 or arrays[i].find(f'Khoản {int_to_roman(current_article_id + 1)}') == 0 or arrays[i].find('Điều thứ') == 0:
                    if current_article_id > 0 and can_add_article:
                        data['articles'].append({
                            "article_id": str(current_article_id) if current_chapter_id == -1 else f"{str(current_chapter_id)}.{str(current_article_id)}",
                            "title": current_article_title,
                            "text": '\n'.join(content)
                        })
                    can_add_article = True
                    current_article_id += 1
                    if ':' in arrays[i]: current_article_title = ' '.join(arrays[i].split(':')[1:]).strip()
                    else: current_article_title = ' '.join(arrays[i].split('.')[1:]).strip()
                    content = []
                elif (have_articles and arrays[i].find('Điều') == 0) or (not have_articles and arrays[i].find(str(current_article_id + 1)) == 0):
                    if  current_article_id > 0 and can_add_article:
                        data['articles'].append({
                            "article_id": str(current_article_id) if current_chapter_id == -1 else f"{str(current_chapter_id)}.{str(current_article_id)}",
                            "title": current_article_title,
                            "text": '\n'.join(content)
                        })
                    can_add_article = True
                    current_article_id += 1
                    if have_articles: current_article_title = ' '.join(arrays[i].split(' ')[2:])
                    else: current_article_title = ' '.join(arrays[i].split(' ')[1:])
                    content = []
                    
                else:
                    content.append(arrays[i])
            if current_article_id > 0:
                data["articles"].append({
                    "article_id": str(current_article_id) if current_chapter_id == -1 else f"{str(current_chapter_id)}.{str(current_article_id)}",
                    "title": current_article_title,
                    "text": '\n'.join(content)
                })

    def is_roman_numeral(s):
        roman_numerals = {
            'I': 1,
            'V': 5,
            'X': 10,
            'L': 50,
            'C': 100,
            'D': 500,
            'M': 1000
        }

        for char in s:
            if char not in roman_numerals:
                return False

        return True

    def get_short_words(words):
        ans = ''
        for word in words.split(' '):
            if is_roman_numeral(word): ans += word
            else: ans += word[0]
        return ans

    def handle_get_law(start, end):
        data = {}
        data["articles"] = []
        data['chapters'] = []
        if start <= 6: data['law_id'] = general_title
        else: data['law_id'] = general_title + "/" + get_short_words(arrays[start])
        global have_articles
        have_articles = check_have_articles(start, end)
        handle_get_articles_and_chapters(start, end, data)
        final_data.append(data)
        
    if __name__ == '__main__':
        if not (value is not None and 'Văn bản này đang cập nhật Nội dung' in value):
            title = soup.title.string.strip().upper()
            general_title = title.split(' ')[2]
            if '/' not in general_title:
                general_title = ''
                for text in title.split(' ')[:2]:
                    general_title += text[0]
                metadata = soup.select('meta[name="Keywords"]')[0]['content']
                # print(metadata)
                pattern = r"\d{2}/\d{2}/\d{4}"
                matches = re.findall(pattern, metadata)
                if matches:
                    general_title = matches[0] + '/' + general_title
            print(general_title)
            contents = soup.select("div#tab1 div.content1 > div > div > div > *")
            contents2 = soup.select("div#tab1 div.content1 > div > div > *")
            if contents2[0].name == 'table':
                print('1')
                if contents2[1].name == 'div':
                    for tag in contents:
                        if tag.name == 'p' and not tag.find("img"):
                            arrays.append(tag.get_text().replace("\n", " ").strip())
                else:
                    for tag in contents2:
                        if tag.name == 'p' and not tag.find("img"):
                            arrays.append(tag.get_text().replace("\n", " ").strip())         
            elif contents2[0].name == 'div':
                print('2')
                if len(contents2) <= 2:
                    for tag in contents:
                        if tag.name == 'p' and not tag.find("img"):
                            arrays.append(tag.get_text().replace("\n", " ").strip())
                else:
                    for tag in contents:
                        if tag.name == 'p' and not tag.find("img"):
                            arrays.append(tag.get_text().replace("\n", " ").strip())
                    for tag in contents2:
                        if tag.name == 'p' and not tag.find("img"):
                            arrays.append(tag.get_text().replace("\n", " ").strip())
            elif contents2[0].name == 'p':
                print(3)
                for tag in contents2:
                    if tag.name == 'p' and not tag.find("img"):
                        arrays.append(tag.get_text().replace("\n", " ").strip())
            start = 2
            law_arr = []
            # print(arrays)
            while len(arrays) > 0 and arrays[-1] == '':
                arrays.pop()
            arrays.append('')
            while('' in arrays[start:]):
                end = arrays.index('', start)
                start
                if not (start <= 6 and end - start < 4):
                    law_arr.append((start, end))
                start = end + 1
            
            # if len(law_arr) >= 2: del law_arr[1]
            for pair in  law_arr:
                handle_get_law(pair[0], pair[1])
    print('continuing, ...', i)
output_file_path = './test.json'
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write(json.dumps(final_data, ensure_ascii=False) + '\n')
print("Dữ liệu đã được ghi tiếp vào file JSON thành công.")

    

