from bs4 import BeautifulSoup
import json

final_data = []
count = 0
for i in range(1, 200):
    file_path = f"./data/page{i}.html"
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    value = soup.select_one(".content1 div:first-child b:nth-of-type(1)").text
    def find_start_position(arrays):
        for i in range(len(arrays)):
            if arrays[i].find("Điều") == 0:
                return i
        return -1

    def handle_get_articles(data, arrays):
        start_position = find_start_position(arrays)
        if start_position != -1:
            current_article_id = 0
            current_article_title = ""
            content = []
            for i in range(start_position, len(arrays)):
                if arrays[i] == '':
                    break
                if arrays[i].find('Điều') == 0:
                    if current_article_id != 0:
                        data["articles"].append({
                            "article_id": current_article_id,
                            "title": current_article_title,
                            "content": '\n'.join(content)
                        })
                    content = []
                    current_article_id += 1
                    current_article_title = ' '.join(arrays[i].split(' ')[2:])
                else:
                    content.append(arrays[i])
            if current_article_id > 0:
                data["articles"].append({
                    "article_id": current_article_id,
                    "title": current_article_title,
                    "content": '\n'.join(content)
                })
    if __name__ == '__main__':
        if not (value is not None and 'Văn bản này đang cập nhật Nội dung' in value):
            data = {}
            data['law_id'] = soup.title.string.split(' ')[2]
            contents = soup.select("div#tab1 div.content1 > div > div > div > *")
            if contents is None or contents == []: contents = soup.select("div#tab1 div.content1 > div > div > *")
            arrays = []
            data["articles"] = []
            for tmp in contents:
                arrays.append(tmp.get_text().replace("\n", " ").strip())
            handle_get_articles(data, arrays)
            final_data.append(data)
        count += 1
        print('continuing...', count)

output_file_path = './output.json'
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write(json.dumps(final_data, ensure_ascii=False) + '\n')
print("Dữ liệu đã được ghi tiếp vào file JSON thành công.")
    

