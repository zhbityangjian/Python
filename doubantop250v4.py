import os
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from termcolor import colored


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}

def get_data(pages):
    data = []
    for page in range(1, pages+1):
        url = 'https://movie.douban.com/top250'
        params = {'start': (page-1)*25}
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                items = soup.find_all('div', class_='item')
                for item in items:
                    movie = item.find('span', class_='title').get_text()
                    year_str = item.find('div', class_='bd').find('p').get_text().strip()
                    year = re.search(r'(\d{4})', year_str).group(1)
                    score = item.find('span', class_='rating_num').get_text()
                    votes = item.find('div', class_='star').find_all('span')[-1].get_text()[:-3]
                    comment = item.find('span', class_='inq')
                    if comment:
                        comment = comment.get_text()
                    else:
                        comment = ""
                    data.append([movie, year, score, votes, comment])
                    
                    # 爬取电影的时候，终端提示信息
                    print(f'成功爬取第{str(len(data)).zfill(3)}部电影:({score}分) {movie} （{comment}）')
            else:
                raise ValueError(f"Error: Could not fetch the page, status code is {response.status_code}")
        except Exception as e:
            raise ValueError(f"Error: Could not fetch the page, {str(e)}")
    return data

def save_to_excel(pages, filename):
    # Get data
    data = get_data(pages)
    columns = ['电影名称', '上映时间', '评分', '评分人数', '简评']
    df = pd.DataFrame(data, columns=columns)
    # Save to xlsx file
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{filename}.xlsx')
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f'保存成功: {filename}')

if __name__ == '__main__':
    pages = 10
    filename = '豆瓣电影排行榜'
    save_to_excel(pages,filename)
