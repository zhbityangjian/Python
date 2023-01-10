import os
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import logging

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}

logging.basicConfig(filename='doubanError.log', level=logging.ERROR)

def parse_movie(item):
    movie = {}
    try:
        # 电影名称
        title = item.find('span', class_='title')
        movie['电影名称'] = title.get_text()

        # 上映时间
        year_str = item.find('div', class_='bd').find('p').get_text().strip()
        year = re.search(r'(\d{4})', year_str).group(1)
        movie['上映时间'] = year

        # 评分
        score = item.find('span', class_='rating_num').get_text()
        movie['评分'] = score

        # 评分人数
        votes = item.find('div', class_='star').find_all('span')[-1].get_text()[:-3]
        movie['评分人数'] = votes

        # 简评
        comment = item.find('span', class_='inq')
        if comment:
            comment = comment.get_text()
        else:
            comment = ""
        movie['简评'] = comment

        # 导演
        director = re.search(r'导演: (.+?) ',year_str)
        if director:
            if '/' in director.group(1):
                for d in director.group(1).split('/'):
                    if ' ' not in d:
                        director=d
        else:
            director = ""
        movie['导演'] = director

        # 主演
        actors = re.search(r'主演: (.+)', year_str)
        if actors:
            actors = actors.group(1)
            actors = actors.split('/')
            for i in range(len(actors)):
                if ' ' not in actors[i]:
                    actors = actors[i]
                    break
                else:
                    actors = actors[i].split()[0]
        else:
            actors = ""
        movie['主演'] = actors

        # 制片国家
        country = re.search(r'制片国家/地区: (.+)', year_str)
        if country:
            country = country.group(1)
            country = country.split('/')[0].strip()
        else:
            country = ""
        movie['制片国家'] = country
    except Exception as e:
        logging.error(f"Error: Could not parse movie, {str(e)}")

    return movie

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
                    movie_data = parse_movie(item)
                    data.append([
                        movie_data['电影名称'],
                        movie_data['上映时间'],
                        movie_data['评分'],
                        movie_data['评分人数'],
                        movie_data['简评'],
                        movie_data['导演'],
                        movie_data['主演'],
                        movie_data['制片国家']
                    ])

                    print(f'成功爬取第{str(len(data)).zfill(3)}部电影:「豆瓣{movie_data["评分"]}--{movie_data["电影名称"]}」 {movie_data["简评"]}')
            else:
                raise ValueError(f"Error: Could not fetch the page, status code is {response.status_code}")
        except Exception as e:
            logging.error(f"Error: Could not fetch the page, {str(e)}")
    return data

def save_to_excel(pages, filename):
    # Get data
    data = get_data(pages)
    columns = [
        '电影名称',
        '上映时间',
        '评分',
        '评分人数',
        '简评',
        '导演',
        '主演',
        '制片国家'
    ]
    df = pd.DataFrame(data, columns=columns)
    # Save to xlsx file
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{filename}.xlsx')
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f'保存成功: {filename}')

if __name__ == '__main__':
    # set up logging
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "doubanError.log")
    logging.basicConfig(level=logging.ERROR, filename=log_file, filemode="w",
                        format="%(asctime)s - %(levelname)s: %(message)s")

    pages = 10
    filename = '豆瓣电影排行榜'
    save_to_excel(pages,filename)
