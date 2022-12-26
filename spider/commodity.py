import json

from spider.tb_login import LoginTaoBao, SpiderSession


class Item(object):

    def __init__(self):
        self.login = LoginTaoBao(SpiderSession())
        self.session = self.login.session

    def get_item(self):
        """

        :return:
        """
        url = 'https://item.taobao.com/item.htm?id=629557122435'
        response = self.session.get(url=url)
        response.text()
        print(response)

    def buy(self):
        headers = {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'referer': 'https://cart.taobao.com/cart.htm',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'image',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'cross-site',

        }
        url = 'https://cart.taobao.com/json/AsyncUpdateCart.do'
        data = {
            '_input_charset': 'utf-8',
            'tk': '51e1573b3b4e',
            'data': json.dumps([{"shopId":"s_385132127","comboId":0,"shopActId":0,"cart":[{"quantity":1,"cartId":"2807316389605","skuId":"4403290001911","itemId":"622135020655"}],"operate":[],"type":"check"}]),
            'shop_id': 0,
            't': 1615197680629,
            'type': 'check',
            'ct': 'f83a04aff851bd5e05974f90cd43adfe',
            'page': 1,
            '_thwlang': 'zh_CN'
        }
        self.session.headers = headers
        # 加入代购买名单
        response = self.session.post(url=url, data=data)
        url = 'https://cashiersa127.alipay.com/standard/fastpay/channelExtInfo.json'
        data = {
            'orderId':'0308ca047d5fc4055c54015465143353',
            'apiCode': 'cmb701',
            'cardNo': '2459',
            'amount': '509.00',
            'ctoken': 'O9ytW8khkJ6YYNRQ'
        }
        response = self.session.post(url=url, data=data)
        print(response.text)



    def get_cart(self):
        url = 'https://cart.taobao.com/cart.htm'
        response = self.session.get(url=url)
        print(response.text)




"""

_input_charset: 
tk: 
data: [{"shopId":"s_1664994355","comboId":0,"shopActId":0,"cart":[{"quantity":1,"cartId":"2807186600699","skuId":"4643812134551","itemId":"629557122435"}],"operate":[],"type":"check"}]
shop_id: 
t: 1615196076127
type: 
ct: 
page: 
_thwlang: 
"""
