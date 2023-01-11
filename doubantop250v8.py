# 这是一个爬取豆瓣Top250列表页的爬虫代码，基本信息获取准确，但是导演、主演、制片国家/地区是一个代码块，只能粗略获取。
# 有问题可以联系zhbityangjian@gmail.com
# 系统库
import os # 提供了不少与操作系统相关联的函数

# 第三方库
import requests # 用来发送 HTTP 请求
from bs4 import BeautifulSoup # 用来解析 HTML 和 XML 文档
import re # 提供正则表达式相关操作
import pandas as pd # 用于数据分析
import logging # 用于记录日志

# 伪装浏览器身份
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}

# 配置 logging 模块来记录错误
logging.basicConfig(filename='doubanError.log', level=logging.ERROR)

# 解析每个电影页面的信息，并且将异常储层到日志文件
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

        # 导演和主演
        director_str = item.find("p", {"class": ""}).text.strip()
        director_name = ""
        main_actor_name = ""

        if '导演:' in director_str:
            director_name = director_str.split('导演:')[1].strip()
        if '主演:' in director_str:
            main_actor_name = director_str.split('主演:')[1].strip()

        if '主演' in director_name:
            director_name = director_name.split('主演')[0].strip()
        if '主' in director_name:
            director_name = director_name.split('主')[0].strip()
        if ' /' in director_name:
            director_name = director_name.split(' /')[0].strip()

        main_actor_name = main_actor_name.split("/")[0].strip()

        movie["导演"] = director_name

        main_actor_name = ""
        if '主演:' in director_str:
            main_actor_name = director_str.split('主演:')[1].split('...')[0].strip()
            main_actor_name = main_actor_name.split("/")[0].strip()
            main_actor_name = re.sub(r'[0-9]+', "", main_actor_name)
        movie["主演"] = main_actor_name
      
        #制片国家/地区
        country = item.find("p", {"class": ""})
        if country:
            country_str = country.text.strip()
            country_name = country_str.split("\xa0/\xa0")[-2].strip()
            movie['制片国家'] = country_name

    except Exception as e:
        logging.error(f"Error: Could not parse movie at {director_name}, {str(e)}") 
        logging.error(f"Error: Could not parse movie at {main_actor_name}, {str(e)}") 
        logging.error(f"Error: Could not parse movie at {country}, {str(e)}") 

    return movie

# 取每一页的数据，并将其存储在data列表中
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

# 定义了一个数据保存函，把获取到数据用数据帧处理后可以直接保存
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


# 主函数
if __name__ == '__main__':
    # 设置日志错误级别，每次运行都先清空日志
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "doubanError.log")
    logging.basicConfig(level=logging.ERROR, filename=log_file, filemode="w",
                        format="%(asctime)s - %(levelname)s: %(message)s")


    pages = 10                #这里是爬取的页数（可以先用一页测试一下）
    filename = '豆瓣电影排行榜' #这里是保存的文件名
    save_to_excel(pages,filename)