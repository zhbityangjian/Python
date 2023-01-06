import requests
import openpyxl
from bs4 import BeautifulSoup

BASE_URL = 'https://movie.douban.com/top250'

def fetch_page(url):
    """发送 HTTP GET 请求并返回响应"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    return r.text

def parse_html(html):
    """解析 HTML 页面并提取数据"""
    soup = BeautifulSoup(html, 'html.parser')
    movie_list_soup = soup.find('ol', attrs={'class': 'grid_view'})
    
    movie_list = []
    for movie_li in movie_list_soup.find_all('li'):
        detail = movie_li.find('div', attrs={'class': 'hd'})
        movie_name = detail.find('span', attrs={'class': 'title'}).getText()
        
        info = movie_li.find('div', attrs={'class': 'bd'})
        movie_info = info.find('p').getText().strip()
        movie_star = info.find('div', attrs={'class': 'star'})
        movie_score = movie_star.find('span', attrs={'class': 'rating_num'}).getText()
        try:
            movie_votes = movie_star.find('span', attrs={'class': 'votes'}).getText()[:-3]
        except AttributeError:
            movie_votes = ''
        try:
            movie_quote = info.find('span', attrs={'class': 'inq'}).getText()
        except AttributeError:
            movie_quote = ''
        
        movie = {
            'name': movie_name,
            'info': movie_info,
            'score': movie_score,
            'votes': movie_votes,
            'quote': movie_quote,
        }
        movie_list.append(movie)
    return movie_list

def save_to_excel(movie_list):
    """将电影信息保存到 Excel 工作簿中"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['电影名称', '电影信息', '评分', '简评'])
    for movie in movie_list:
        ws.append([movie['name'], movie['info'], movie['score'], movie['quote']])
    wb.save('movies.xlsx')

def main():
    """爬虫的主函数"""
    url = BASE_URL
    movie_list = []
    while url:
        # 发送 HTTP GET 请求并获取响应
        html = fetch_page(url)
        # 解析 HTML 页面并提取数据
        movies = parse_html(html)
        # 将电影信息添加到 movie_list 列表中
        movie_list.extend(movies)
        print(f'当前爬取到 {len(movie_list)} 部电影')
        # 解析下一页的链接
        soup = BeautifulSoup(html, 'html.parser')
        next_link = soup.find('span', attrs={'class': 'next'}).find('a')
        if next_link:
            url = BASE_URL + next_link['href']
        else:
            url = None
    # 保存电影信息到 Excel 工作簿中
    save_to_excel(movie_list)

if __name__ == '__main__':
    main()