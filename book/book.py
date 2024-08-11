import json
import os
import logging
from urllib3 import disable_warnings
from requests import Session, RequestException
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# 禁用SSL警告，避免在进行HTTPS请求时出现不必要的警告
disable_warnings()

class BookSourceManager:
    def __init__(self, file_path, config):
        """
        初始化BookSourceManager类
        :param file_path: str, 书源文件的路径或URL
        :param config: dict, 包含配置参数的字典
        """
        self.file_path = file_path
        self.config = config
        self.logger = self.setup_logger()
        self.session = self.setup_session()
        # 预处理过滤关键词，转换为小写并存储为集合，提高查找效率
        self.keywords_set = set(keyword.lower() for keyword in self.config.get('keywords_to_filter', []))

    @staticmethod
    def setup_logger():
        """
        设置日志记录器
        :return: logging.Logger对象
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def setup_session(self):
        """
        设置requests会话，用于复用连接，提高网络请求效率
        :return: requests.Session对象
        """
        session = Session()
        session.headers.update({'user-agent': self.config.get('user_agent', 'Mozilla/5.0')})
        session.verify = False  # 禁用SSL验证，注意：这可能带来安全风险
        return session

    def load_books(self):
        """
        从文件或URL加载书源
        :return: list, 包含书源数据的列表
        """
        self.logger.info("正在加载书源...")
        try:
            if self.file_path.startswith('http'):
                response = self.session.get(self.file_path, timeout=self.config.get('timeout', 5))
                response.raise_for_status()
                return response.json()
            else:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (RequestException, json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.error(f"加载书源时出错: {str(e)}")
            return []

    def check_book_source(self, book):
        """
        检查单个书源的可用性
        :param book: dict, 包含书源信息的字典
        :return: dict, 包含书源和其状态的字典
        """
        try:
            url = book['bookSourceUrl']
            response = self.session.get(url, timeout=self.config.get('timeout', 5))
            return {'book': book, 'status': response.status_code == 200}
        except RequestException:
            return {'book': book, 'status': False}

    def checkbooks(self, workers):
        """
        并发检查所有书源的可用性
        :param workers: int, 并发工作线程数
        :return: dict, 包含有效和无效书源的字典
        """
        self.logger.info("开始检查书源...")
        books = self.load_books()
        good, error = [], []

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(self.check_book_source, book) for book in books]
            for future in tqdm(as_completed(futures), total=len(books), desc="检查进度"):
                result = future.result()
                (good if result['status'] else error).append(result['book'])

        return {'good': good, 'error': error}

    @staticmethod
    def dedup(books):
        """
        去除重复的书源
        :param books: list, 书源列表
        :return: list, 去重后的书源列表
        """
        seen_urls = set()
        return [book for book in books if not (book['bookSourceUrl'] in seen_urls or seen_urls.add(book['bookSourceUrl']))]

    def should_filter(self, book):
        """
        判断是否应该过滤掉该书源
        :param book: dict, 书源信息
        :return: bool, 是否应该过滤
        """
        if self.config.get('exact_keyword_match', False):
            return book.get('bookSourceName', '').lower() in self.keywords_set
        else:
            return any(
                keyword in book.get('bookSourceName', '').lower() or
                keyword in book.get('bookSourceUrl', '').lower() or
                keyword in book.get('bookSourceGroup', '').lower() or
                keyword in book.get('bookSourceComment', '').lower()
                for keyword in self.keywords_set
            )

    def filter_sources(self, books):
        """
        根据关键词过滤书源
        :param books: list, 待过滤的书源列表
        :return: list, 过滤后的书源列表
        """
        filtered_books = []
        filtered_out = 0
        for book in books:
            if self.should_filter(book):
                filtered_out += 1
                self.logger.debug(f"已过滤书源: {book.get('bookSourceName', 'Unknown')} 由于关键词匹配")
            else:
                filtered_books.append(book)
        self.logger.info(f"共过滤掉 {filtered_out} 个书源")
        return filtered_books

    def process_books(self, workers):
        """
        处理所有书源：检查、去重、过滤
        :param workers: int, 并发工作线程数
        :return: dict, 处理后的结果
        """
        self.logger.info("开始处理书源...")
        result = self.checkbooks(workers)

        if self.config.get('dedup') == 'y':
            self.logger.info("正在去除重复...")
            result['good'] = self.dedup(result['good'])

        if self.config.get('filter', 'n') == 'y':
            self.logger.info("正在过滤书源...")
            result['good'] = self.filter_sources(result['good'])
            result['error'] = self.filter_sources(result['error'])

        self.logger.info("处理完成！")
        return result

    def save_results(self, results, outpath):
        """
        保存处理结果到文件
        :param results: dict, 处理结果
        :param outpath: str, 输出路径
        """
        self.logger.info("正在保存结果...")
        os.makedirs(outpath, exist_ok=True)
        file_path = os.path.join(outpath, 'valid_books.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(results['good'], f, ensure_ascii=False, indent=4, sort_keys=False)
        self.logger.info(f"有效书源已保存到 {file_path}")

    def analyze_results(self, results):
        """
        分析处理结果，提供统计信息
        :param results: dict, 处理结果
        :return: dict, 包含统计信息的字典
        """
        total = len(results['good']) + len(results['error'])
        success_rate = len(results['good']) / total * 100 if total > 0 else 0
        self.logger.info(f"总书源数: {total}")
        self.logger.info(f"有效书源数: {len(results['good'])}")
        self.logger.info(f"无效书源数: {len(results['error'])}")
        self.logger.info(f"成功率: {success_rate:.2f}%")
        return {
            'total': total,
            'valid': len(results['good']),
            'invalid': len(results['error']),
            'success_rate': success_rate
        }
