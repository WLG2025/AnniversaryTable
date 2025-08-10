"""
工具后台入口
"""
import json
from datetime import datetime
from http import HTTPStatus
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

from zhdate import ZhDate

# 访问端口
SERVER_PORT = 12345


def calc_left(date_int, lunar=False):
    """
    计算给定纪念日期距离现在的秒数，只取给定日期的月日来算
    :param date_int: 给定日期 yyyymmdd 整数
    :param lunar: 是否为农历日期
    :return:
    """
    now_date = datetime.now()
    now_year = now_date.year
    now_time = now_date.timestamp()
    if lunar:  # 农历
        try:
            lunar_date = ZhDate(now_year, int((date_int % 10000) / 100), int(date_int % 100))
            dst_timestamp = lunar_date.to_datetime().timestamp()  # 转公历
            if now_time >= dst_timestamp:
                # 年份+1
                lunar_date = ZhDate(now_year + 1, int((date_int % 10000) / 100), int(date_int % 100))
                dst_timestamp = lunar_date.to_datetime().timestamp()
            return dst_timestamp - now_time
        except Exception as err:
            print('parse lunar date except|{}|{}'.format(err, date_int))
            return 0
    else:
        date_str = '{:04d}{:02d}{:02d}'.format(now_year, int((date_int % 10000) / 100), int(date_int % 100))
        dst_timestamp = datetime.strptime(date_str, '%Y%m%d').timestamp()
        if now_time >= dst_timestamp:
            # 年份+1
            date_str = '{:04d}{:02d}{:02d}'.format(now_year + 1, int((date_int % 10000) / 100), int(date_int % 100))
            dst_timestamp = datetime.strptime(date_str, '%Y%m%d').timestamp()
        return dst_timestamp - now_time


class GlobalResource(object):
    def __init__(self):
        # self.index_html = self.make_index()
        # self.main_js = self.load_file('main.js')
        # print('global resource ok')
        pass

    @staticmethod
    def make_index():
        """
        生成主页模板
        :return:
        """
        index_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf8">
    <title>欢迎使用周年日工具</title>
    <link rel="stylesheet" type="text/css" href="/main.css">
    <script type="text/javascript" src="/main.js"></script>
</head>
<body>
    <div id="app"></div>
</body>
</html>
"""
        return index_html

    @staticmethod
    def load_file(filename):
        """
        加载静态资源文件
        :param filename: 文件名
        :return:
        """
        try:
            with open(filename, 'r', encoding='utf8') as fin:
                return fin.read()
        except Exception as err:
            print('load {} except|{}'.format(filename, err))
            return 'let msg="load {} except"'.format(filename)

    @staticmethod
    def load_config():
        """
        加载配置信息
        :return:
        """
        dates = []
        try:
            with open('config.conf', 'r', encoding='utf8') as fin:
                for line in fin:
                    try:
                        tmp = line.strip().split('|')
                        if len(tmp) != 3:
                            continue
                        lunar = True if tmp[1].strip() == '农历' else False
                        date_int = int(tmp[2].strip())
                        dates.append([
                            tmp[0].strip(), lunar,
                            '{:04d}-{:02d}-{:02d}'.format(int(date_int / 10000), int((date_int % 10000) / 100), int(date_int % 100)),
                            int(calc_left(date_int, lunar))
                        ])
                    except Exception as err:
                        print('parse line failed|{}|line:{}'.format(err, line))
                        continue
        except Exception as err:
            print('load config except|{}'.format(err))
        return dates


# 管理全局信息
gr = GlobalResource()


class MyHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol_version = 'HTTP/1.1'

    def return_common(self, data, ctype=None):
        """
        返回响应信息
        :param data: 返回的字符串数据
        :param ctype: 返回的媒体类型
        :return:
        """
        self.send_response(HTTPStatus.OK)

        if not ctype:
            ctype = 'application/json; charset=utf-8'
        body = data.encode('utf8')

        self.send_header("Content-type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def do_HEAD(self):
        """
        处理HEAD请求
        :return:
        """
        self.return_common('head ok')

    def do_GET(self):
        """
        处理GET请求
        :return:
        """
        if self.path == '/' or self.path == '/index' or self.path == '/index.htm' or self.path == '/index.html':
            self.return_common(gr.make_index(), 'text/html; charset=utf-8')
            return
        elif self.path == '/main.js':
            self.return_common(gr.load_file('main.js'), 'application/javascript; charset=utf-8')
            return
        elif self.path == '/main.css':
            self.return_common(gr.load_file('main.css'), 'text/css; charset=utf-8')
            return
        self.return_common('get ok')

    def do_POST(self):
        """
        处理POST请求
        :return:
        """
        if self.path == '/config':
            self.return_common(json.dumps(gr.load_config(), ensure_ascii=False, separators=(',', ':')))
            return
        self.return_common('post ok')


def main():
    try:
        print('OK，请用浏览器打开 http://127.0.0.1:{} 来访问'.format(SERVER_PORT))
        with ThreadingHTTPServer(('0.0.0.0', SERVER_PORT), MyHandler) as app:
            app.serve_forever()
    except KeyboardInterrupt as err:
        print('ctrl-c, quit|{}'.format(err))
    except Exception as err:
        print('except, quit|{}'.format(err))


if __name__ == '__main__':
    main()
