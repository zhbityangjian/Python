import re
import time
import os
from datetime import datetime

# 导入第三方库
from bs4 import BeautifulSoup
import pandas as pd
import openpyxl
import requests

# 定义常量
FIRST_PAGE = 0  # 第一页
LAST_PAGE = 9  # 最后一页
SLEEP_TIME = 2  # 爬取下一页数据时的休眠时间

def main():
    """
    主函数
    """
    # 获取当前日期
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")  # 将日期格式化为字符串

    # 拼接文件名
    filename = f"豆瓣Top250电影{date_str}.xlsx"
    save_path = os.path.join(os.getcwd(), filename)

    # 判断文件是否存在
    if os.path.exists(save_path):
        # 删除文件
        os.remove(save_path)

    movie_url ="https://movie.douban.com/top250?start="
    # 获取电影信息
    data = fetch_data(movie_url)
    # 保存数据到 Excel
    save_data(data, save_path)
    print("数据爬取成功，数据存放在了 {}".format(save_path))


def fetch_data(movie_url):
    """
    获取电影信息
    """
    data_list = []
    for page in range(FIRST_PAGE, LAST_PAGE+1):
        time.sleep(SLEEP_TIME)
        url = movie_url + str(page * 25)
        html = fetch_url(url)
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all('div', class_="item"):
            data = []
            item = str(item)
            # 提取电影名
            titles = re.findall(r'<span class="title">(.*?)</span>', item)
            if (len(titles) == 2):
                ctitle = titles[0]
                data.append(ctitle)
                otitle = titles[1].replace("/", "")
                data.append(otitle)
            else:
                data.append(titles[0])
                data.append('')
            # 提取评分
            data.append(re.findall(r'<span class="rating_num" property="v:average">(.*)</span>', item)[0])
            # 提取评价数
            data.append(re.findall(r'<span>(\d*)人评价</span>', item)[0])
            # 提取精华短评
            inq = re.findall(r'<span class="inq">(.*)</span>', item)
            if inq:
                data.append(inq[0])
            else:
                data.append('')
            data_list.append(data)
            print("获取第 {} 条信息：电影名：{}，评分：{}".format(len(data_list), data[0], data[2]))

    # 创建数据帧
    df = pd.DataFrame(data_list, columns=['电影名', '外语电影名', '评分', '评价数', '精华短评'])
    return df

def save_data(data, save_path):
    """
    保存数据到 Excel
    """
    data.to_excel(save_path, index=False)

def fetch_url(url):
    """
    获取网页 HTML
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    return response.text

if __name__ == '__main__':
    main()

