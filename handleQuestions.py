from bs4 import BeautifulSoup
import json

final_data = []
count = 0
file_path = f"./questions/vuongmacphaply/1.html"
with open(file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()
soup = BeautifulSoup(html_content, 'html.parser')
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
    data = {}
    data['law_id'] = soup.title.string.split(' ')[2]
    contents = soup.select(".article__sapo.article__body > *")
    arrays = []
    data["articles"] = []
    print(arrays)
    for tmp in contents:
        if tmp.name == 'p':
            arrays.append(tmp.get_text().replace("\n", " ").strip())
    # handle_get_articles(data, arrays)
    for text in contents:
        print(text)
    data['1'] = '2'  
    final_data.append(data)
    count += 1
    print('continuing...', count)

output_file_path = './output.json'
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write(json.dumps(final_data, ensure_ascii=False) + '\n')
print("Dữ liệu đã được ghi tiếp vào file JSON thành công.")
    

