import os
import datetime
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import logging
import time
from random import randint

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}

# 配置 logging 模块来记录错误
logging.basicConfig(filename='doubanError.log', level=logging.ERROR)

# 解析每个电影的信息
def parse_movie(item, movie_count):
    movie = {}
    try:
        # 电影名称
        title = item.find('span', class_='title').get_text()
        movie['电影名称'] = title

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
        movie['简评'] = comment.get_text() if comment else "无简评"

        # 导演和主演
        director_actors_pattern = re.compile(r"导演: (.*?)\s*(?:主演: (.*))?\s*(\d{4})")
        director_str = item.find("p", {"class": ""}).text.strip()
        match = director_actors_pattern.search(director_str)
        if match:
            movie["导演"] = match.group(1).strip()
            movie["主演"] = match.group(2).strip() if match.group(2) else ''

        # 制片国家
        country_str = item.find("p", {"class": ""}).text.strip()
        country_name = country_str.split("/")[-2].strip() if "/" in country_str else ''
        movie['制片国家'] = country_name

        # 打印爬取进度，按电影输出进度信息，并包括简评
        print(f'爬取进度: 第{movie_count}部电影: 「{movie["电影名称"]}」, 简评: {movie["简评"]}')

    except Exception as e:
        logging.error(f"Error parsing movie: {str(e)}")
        logging.error(f"Movie data: {movie}")

    return movie

# 获取所有页面的数据
def get_data(pages):
    data = []
    movie_count = 0
    for page in range(1, pages+1):
        url = 'https://movie.douban.com/top250'
        params = {'start': (page-1)*25}
        for attempt in range(3):  # 最多重试3次
            try:
                response = requests.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    items = soup.find_all('div', class_='item')
                    for item in items:
                        movie_count += 1
                        movie_data = parse_movie(item, movie_count)
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
                        # 每爬取一部电影后等待1秒，控制输出节奏
                        time.sleep(1)
                    break  # 当前页面成功获取，跳出重试循环
                else:
                    logging.error(f"Error: Status code {response.status_code} for {url}")
            except Exception as e:
                logging.error(f"Error fetching {url}: {str(e)}")
            time.sleep(randint(1, 3))  # 每次重试前等待随机时间

    return data

# 保存数据到Excel文件
def save_to_excel(pages, filename):
    data = get_data(pages)
    columns = ['电影名称', '上映时间', '评分', '评分人数', '简评', '导演', '主演', '制片国家']
    df = pd.DataFrame(data, columns=columns)
    today = datetime.date.today().strftime('%Y%m%d')
    filename_with_date = f'{filename}_{today}.xlsx'
    save_path = os.path.join(os.getcwd(), filename_with_date)
    df.to_excel(save_path, index=False, engine='openpyxl')
    print(f'保存成功: {save_path}') 

# 主函数
if __name__ == '__main__':
    # 设置日志错误级别，每次运行都先清空日志
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "doubanError.log")
    logging.basicConfig(level=logging.ERROR, filename=log_file, filemode="w",
                        format="%(asctime)s - %(levellevel)s: %(message)s")

    # 爬取豆瓣Top250的所有数据
    pages = 10                # 每页25部电影，10页共250部
    filename = '豆瓣电影排行榜'  # 保存文件的名称
    save_to_excel(pages, filename)
