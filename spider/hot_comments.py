# -*- coding: utf-8 -*-
"""
豆瓣电影热门短评爬虫
功能：获取豆瓣电影的热门短评数据
作者：AI助手
"""

# ============ 导入必要的库 ============
import requests  # [库] 用于发送HTTP请求，获取网页数据
import time  # [库] 用于控制爬虫速度，避免请求过快被封禁
import json  # [库] 用于处理JSON格式数据
import random  # [库] 用于生成随机数，模拟人类行为
from typing import List, Dict  # [语法: 类型提示] 用于标注函数的参数和返回值类型，提高代码可读性


class DoubanCommentSpider:
    """
    [类] 豆瓣电影短评爬虫类
    
    这个类封装了爬取豆瓣电影短评的所有功能
    """
    
    def __init__(self, movie_id: str, max_page: int = 19):
        """
        [构造函数] 初始化爬虫对象
        
        参数 (Input):
            movie_id: str - 电影ID，例如 '1292052' (代表《肖申克的救赎》)
            max_page: int - 最大爬取页数，默认19页
        """
        self.movie_id = movie_id  # [语法: self] 实例变量，存储电影ID
        self.max_page = max_page  # [语法: self] 实例变量，存储最大页数
        self.base_url = 'https://movie.douban.com/subject/{}/comments'.format(movie_id)  # [功能] 构造基础URL
        
        # [知识点: HTTP请求头] 模拟浏览器访问，避免被识别为爬虫
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webview,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        }
        
        self.all_comments = []  # [语法: list] 存储所有爬取到的短评数据
    
    
    def get_page_comments(self, page: int = 0) -> List[Dict]:
        """
        [函数] 获取指定页的短评数据
        
        算法思路:
        1. 构造带分页参数的URL
        2. 发送HTTP GET请求
        3. 解析返回的HTML或JSON数据
        4. 提取短评信息
        
        参数 (Input):
            page: int - 页码，从0开始
            
        返回值 (Output):
            List[Dict] - 短评列表，每条短评是一个字典，包含用户名、评分、内容等信息
        """
        try:  # [语法: try-except] 异常处理，捕获网络请求可能出现的错误
            # [功能] 构造分页URL，start参数控制从第几条开始
            # 每页20条，所以第1页start=0, 第2页start=20, 第3页start=40...
            params = {
                'start': page * 20,  # [计算] 计算起始位置
                'limit': 20,  # [参数] 每页显示数量
                'status': 'P',  # [参数] P表示看过的短评（热门短评）
                'sort': 'new_score',  # [参数] 按热度排序
            }
            
            # [语法: f-string] 格式化字符串，输出当前爬取进度
            print(f'正在爬取第 {page + 1} 页...')
            
            # [功能] 发送GET请求获取网页数据
            # timeout=10 表示10秒超时
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            # [知识点: HTTP状态码] 200表示请求成功
            if response.status_code == 200:
                # [功能] 设置正确的编码，避免中文乱码
                response.encoding = 'utf-8'
                
                # [功能] 解析HTML内容，提取短评数据
                comments = self._parse_comments(response.text)
                
                print(f'第 {page + 1} 页爬取成功，获得 {len(comments)} 条短评')
                
                return comments  # [语法: return] 返回解析后的短评列表
            else:
                print(f'请求失败，状态码: {response.status_code}')
                return []  # [语法: return] 返回空列表
                
        except requests.exceptions.Timeout:  # [异常处理] 捕获超时错误
            print(f'第 {page + 1} 页请求超时')
            return []
        except requests.exceptions.RequestException as e:  # [异常处理] 捕获其他网络错误
            print(f'第 {page + 1} 页请求出错: {str(e)}')
            return []
    
    
    def _parse_comments(self, html_content: str) -> List[Dict]:
        """
        [私有函数] 解析HTML内容，提取短评数据
        
        [命名规范: _开头] 表示这是一个私有方法，通常只在类内部使用
        
        参数 (Input):
            html_content: str - HTML网页源代码
            
        返回值 (Output):
            List[Dict] - 短评列表
        """
        from bs4 import BeautifulSoup  # [库] BeautifulSoup用于解析HTML，需要先安装: pip install beautifulsoup4
        
        comments = []  # [语法: list] 初始化空列表
        
        # [功能] 创建BeautifulSoup对象，解析HTML
        # 'html.parser' 是Python内置的解析器
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # [功能] 找到所有的短评项
        # class_='comment-item' 表示查找class属性为'comment-item'的元素
        comment_items = soup.find_all('div', class_='comment-item')
        
        # [语法: for循环] 遍历每一条短评
        for item in comment_items:
            try:  # [异常处理] 防止某条短评解析失败影响整体
                # [功能] 提取短评ID
                comment_id = item.get('data-cid', '')  # [方法: get] 获取属性值，如果不存在返回''
                
                # [功能] 提取用户信息
                user_info = item.find('span', class_='comment-info')
                username = user_info.find('a').text.strip() if user_info and user_info.find('a') else '匿名'  # [语法: 三元表达式] if条件 else语句
                
                # [功能] 提取评分
                rating_tag = item.find('span', class_='rating')
                rating = ''
                if rating_tag:
                    # [功能] 评分在class属性中，如'allstar50'表示5星
                    rating_classes = rating_tag.get('class', [])
                    for cls in rating_classes:
                        if cls.startswith('allstar'):  # [方法: startswith] 检查字符串是否以指定内容开头
                            rating_num = cls.replace('allstar', '')  # [方法: replace] 替换字符串
                            rating = int(rating_num) // 10  # [运算符: //] 整数除法，如50//10=5
                            break
                
                # [功能] 提取短评内容
                comment_content_tag = item.find('span', class_='short')
                comment_content = comment_content_tag.text.strip() if comment_content_tag else ''
                
                # [功能] 提取点赞数（有用数）
                vote_tag = item.find('span', class_='votes vote-count')
                votes = int(vote_tag.text.strip()) if vote_tag else 0  # [类型转换: int()] 将字符串转为整数
                
                # [功能] 提取发表时间
                time_tag = item.find('span', class_='comment-time')
                comment_time = time_tag.get('title', '').strip() if time_tag else ''
                
                # [语法: 字典] 将提取的信息组织成字典结构
                comment_dict = {
                    'comment_id': comment_id,  # 短评ID
                    'username': username,  # 用户名
                    'rating': rating,  # 评分（1-5星）
                    'content': comment_content,  # 短评内容
                    'votes': votes,  # 点赞数
                    'time': comment_time,  # 发表时间
                }
                
                comments.append(comment_dict)  # [方法: append] 将字典添加到列表末尾
                
            except Exception as e:  # [异常处理] 捕获所有异常
                print(f'解析某条短评时出错: {str(e)}')
                continue  # [语法: continue] 跳过当前循环，继续下一次
        
        return comments  # [语法: return] 返回解析结果
    
    
    def crawl_all(self) -> List[Dict]:
        """
        [函数] 爬取所有页的短评数据
        
        算法思路:
        1. 循环遍历所有页码
        2. 每页爬取完后随机暂停1-3秒（模拟人类行为）
        3. 将所有短评汇总到一个列表
        
        返回值 (Output):
            List[Dict] - 所有短评的列表
        """
        print(f'='*50)  # [功能] 打印分隔线，美化输出
        print(f'开始爬取电影ID: {self.movie_id} 的热门短评')
        print(f'计划爬取 {self.max_page} 页')
        print(f'='*50)
        
        # [语法: range()] 生成数字序列，range(19)生成0到18
        for page in range(self.max_page):
            # [功能] 获取当前页的短评
            page_comments = self.get_page_comments(page)
            
            # [语法: extend] 将page_comments列表中的元素逐个添加到all_comments
            # 区别于append: append会把整个列表作为一个元素添加
            self.all_comments.extend(page_comments)
            
            # [知识点: 爬虫礼貌] 随机暂停1-3秒，避免请求过快被封IP
            # random.uniform(1, 3) 生成1到3之间的随机浮点数
            sleep_time = random.uniform(1, 3)
            print(f'暂停 {sleep_time:.2f} 秒...\n')  # [格式化: :.2f] 保留2位小数
            time.sleep(sleep_time)  # [功能] 程序暂停指定秒数
        
        print(f'='*50)
        print(f'爬取完成！共获得 {len(self.all_comments)} 条短评')
        print(f'='*50)
        
        return self.all_comments  # [语法: return] 返回所有短评
    
    
    def save_to_json(self, filename: str = 'douban_comments.json'):
        """
        [函数] 将短评数据保存为JSON文件
        
        参数 (Input):
            filename: str - 保存的文件名，默认'douban_comments.json'
        """
        try:
            # [语法: with open] 上下文管理器，自动关闭文件
            # 'w'表示写入模式，encoding='utf-8'确保中文正常保存
            with open(filename, 'w', encoding='utf-8') as f:
                # [功能] 将Python对象转换为JSON格式并写入文件
                # ensure_ascii=False: 确保中文不被转为Unicode编码
                # indent=4: 美化输出，每层缩进4个空格
                json.dump(self.all_comments, f, ensure_ascii=False, indent=4)
            
            print(f'数据已保存到文件: {filename}')
            
        except Exception as e:  # [异常处理] 捕获文件写入错误
            print(f'保存文件时出错: {str(e)}')
    
    
    def save_to_csv(self, filename: str = 'douban_comments.csv'):
        """
        [函数] 将短评数据保存为CSV文件
        
        [知识点: CSV] CSV是逗号分隔值文件，可用Excel打开，适合表格数据
        
        参数 (Input):
            filename: str - 保存的文件名，默认'douban_comments.csv'
        """
        import csv  # [库] Python内置的CSV处理库
        
        try:
            # [语法: with open] 打开文件用于写入
            # newline='' 避免Windows系统出现空行
            with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
                # [知识点: utf-8-sig] 带BOM的UTF-8编码，让Excel正确识别中文
                
                if not self.all_comments:  # [语法: if not] 检查列表是否为空
                    print('没有数据可保存')
                    return  # [语法: return] 提前退出函数
                
                # [功能] 定义CSV文件的列名
                fieldnames = ['comment_id', 'username', 'rating', 'content', 'votes', 'time']
                
                # [功能] 创建CSV写入器
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # [功能] 写入表头（列名）
                writer.writeheader()
                
                # [功能] 逐行写入数据
                writer.writerows(self.all_comments)
            
            print(f'数据已保存到文件: {filename}')
            
        except Exception as e:  # [异常处理] 捕获文件写入错误
            print(f'保存CSV文件时出错: {str(e)}')


# ============ 主程序入口 ============
def main():
    """
    [函数] 主函数 - 程序的执行入口
    
    [知识点: 主函数] 将主要逻辑封装在main()中是Python的最佳实践
    """
    # [配置] 设置要爬取的电影ID
    # 示例：'1292052' 是《肖申克的救赎》的豆瓣ID
    # 你可以访问豆瓣电影页面，从URL中获取电影ID
    # 例如: https://movie.douban.com/subject/1292052/ 中的 1292052
    movie_id = '34780991'
    
    # [配置] 设置爬取页数，默认19页（约380条短评）
    max_page = 19
    
    # [实例化] 创建爬虫对象
    # [语法: 类()] 调用类的构造函数创建实例
    spider = DoubanCommentSpider(movie_id=movie_id, max_page=max_page)
    
    # [执行] 开始爬取
    spider.crawl_all()
    
    # [保存] 保存为JSON格式
    spider.save_to_json(f'movie_{movie_id}_comments.json')
    
    # [保存] 保存为CSV格式（可用Excel打开）
    spider.save_to_csv(f'movie_{movie_id}_comments.csv')


# ============ 程序执行检查 ============
# [知识点: __name__] 当直接运行此文件时，__name__的值为'__main__'
# 如果此文件被其他文件导入，__name__的值为文件名'hot_comments'
# 这样可以防止导入时自动执行main()
if __name__ == '__main__':
    main()  # [执行] 调用主函数
