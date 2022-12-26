import os
import pickle
import re
import time

import requests

from spider.dispose import Image, TaoBaoException
from setting import COOKIES_FILE_PATH, QRCODE_PATH, LOGIN_QR
from log.taobao_logger import logger


class SpiderSession(object):
    def __init__(self):
        self.cookie_file_path = COOKIES_FILE_PATH
        self._session = self._init_session()

    def get_headers(self):
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        }

    def _init_session(self):
        session = requests.session()
        session.headers = self.get_headers()
        return session

    def update_cookies(self, cookies):
        self._session.cookies.update(cookies)

    def get_cookies(self):
        return self._session.cookies

    def get_session(self):
        return self._session

    def save_cookies_file(self):
        """

        :param file_path: 保存cookies的路径
        :return:
        """

        directory = os.path.dirname(self.cookie_file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(self.cookie_file_path, 'wb') as file:
            pickle.dump(self.get_cookies(), file)

    def get_cookies_local(self):
        """
        获取本地cookies
        :return:
        """

        if not os.path.exists(self.cookie_file_path):
            return False
        with open(self.cookie_file_path, 'rb') as file:
            cookies = pickle.load(file)
            self.update_cookies(cookies)
        return True


class LoginTaoBao(object):

    def __init__(self, spider_session: SpiderSession):
        self.spider_session = spider_session
        self.session = self.spider_session.get_session()
        self.if_login = False
        self.refresh_login_status()

    def refresh_login_status(self):
        """
        判断cookies是否已经过期
        :return:
        """
        if not (self.spider_session.get_cookies_local() and self.get_username()):
            self.login()
        self.if_login = True

    def _save_qrcode(self):
        """
        保存登录二维码
        :param url: 二维码地址
        :return:
        """
        response = self.session.get(url=self.qrcode_url)
        if response.status_code == 200:
            Image.save_(QRCODE_PATH, response)
            logger.info('登录淘宝二维码获取成功，请打开淘宝APP扫码登录！')
            Image.open_(QRCODE_PATH)
        else:
            logger.error('登录淘宝二维码获取失败：{}, {}'.format(response.status_code, response.text))
            raise

    def _get_qrcode(self):
        """
        获取二维码图片和token
        :return:
        """
        checkQRCodeURL = 'https://qrlogin.taobao.com/qrcodelogin/generateQRCode4Login.do'
        response = self.session.get(url=checkQRCodeURL)
        results = response.json()
        return results

    def _qrcode_status(self):
        """
        获取二维码当前状态
        :param lgToken:
        :return:
        """
        getQRcodeURL = 'https://qrlogin.taobao.com/qrcodelogin/qrcodeLoginCheck.do?lgToken={}'.format(self.lgToken)
        '''
        10000 ：等待扫码
        10001 ：扫码成功，但没在手机端确认登录
        10004 ：二维码过期
        10006 ：登录成功，会返回登录成功后的登录链接'''
        try:
            while True:
                response = self.session.get(url=getQRcodeURL)
                result = response.json()
                code = result['code']
                if code == '10000':
                    logger.info('等待扫码，请尽快扫码，防止过期！')
                elif code == '10001':
                    logger.info('扫码成功，请在手机点击确认登录')
                elif code == '10004':
                    logger.info('二维码过期,请重新获取二维码')
                    raise TaoBaoException('二维码过期请重新启动：{} {}'.format(response.status_code, response.text))
                elif code == '10006':
                    logger.info('扫码成功,获取用户页链接')
                    response = self.session.get(result['url'])
                    if response.status_code != 200:
                        TaoBaoException('访问登录连接失败： {} {}'.format(response.status_code, response.text))
                    return True
                else:
                    raise TaoBaoException('状态码不存在：{} {}'.format(response.status_code, response.text))
                time.sleep(1)
        except Exception as error:
            logger.error(error)
            return False

    def _qrcode_login(self):
        logger.info('二维码登录！')
        results = self._get_qrcode()
        qrcode_url = results['url']
        self.lgToken = results['lgToken']
        self.qrcode_url = 'http:' + qrcode_url
        self._save_qrcode()
        qr_status = self._qrcode_status()
        Image.remove(QRCODE_PATH)
        if not qr_status:
            raise
        self.spider_session.save_cookies_file()
        self.get_username()

    def _user_pwd_login(self):
        print('账户密码登录！')
        pass

    def get_username(self):
        url = 'http://i.taobao.com/my_taobao.htm'
        try:
            response = self.session.get(url)
            response.raise_for_status()
        except Exception as e:
            logger.error(e)
            raise
        # 提取淘宝昵称
        nick_name_match = re.search(r'<input id="mtb-nickname" type="hidden" value="(.*?)"/>', response.text)
        print(nick_name_match)
        if nick_name_match:
            logger.info('登录淘宝成功，你的用户名是：{}'.format(nick_name_match.group(1)))
            return True
        else:
            return False

    def login(self):
        if not self.if_login:
            if LOGIN_QR:
                self._qrcode_login()
            else:
                self._user_pwd_login()
