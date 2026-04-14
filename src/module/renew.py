from src.utils import request


class Renew(object):

    def __init__(self, user_setting: dict, client):
        self.client = client
        self.user_setting = user_setting
        self.headers = request.build_headers(form=True)
        self.param = {
            "iu": "2"
        }
        self.url = "https://www.momozhen.com/fyg_llpw_c.php"

    def run(self):
        print(self.user_setting["username"] + " 开始更新密钥...")
        res = request.post_data(self.url, self.headers, self.param, self.client)
        if res and "ok" in res:
            print(self.user_setting["username"] + " 更新密钥成功！")
            return True
        else:
            print(self.user_setting["username"] + " 更新密钥失败！")
            return False
