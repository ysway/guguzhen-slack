import re

from src.module.battle import Battle
from src.module.factory import Factory
from src.module.renew import Renew
from src.module.shop import Shop
from src.module.wish import Wish
from src.utils import request, config


class Process(object):

    def __init__(self, user_setting: dict):
        self.user_setting = user_setting
        self.headers = request.build_headers()
        self.url = "https://www.momozhen.com/fyg_index.php"
        self.client = None

    def run(self):
        if not self.user_setting["cookie"]:
            print(self.get_display_name() + " 未填写 cookie，已跳过")
            return

        with request.create_client(self.user_setting["cookie"]) as client:
            self.client = client
            user_bool = self.get_user_info()
            if not user_bool:
                print(self.get_display_name() + " 获取用户信息失败！")
                return

            self.persist_cookie("初始化")
            if self.user_setting.get("renew_key", True):
                Renew(self.user_setting, client).run()
                self.persist_cookie("续密钥")

            print(self.user_setting["username"] + " 开始执行日常...")
            Shop(self.user_setting, client).run()
            Wish(self.user_setting, client).run()
            Battle(self.user_setting, client).run()
            Factory(self.user_setting, client).run()
            self.persist_cookie("任务结束")

    def get_user_info(self):
        res = request.get(self.url, self.headers, self.client)
        if not res:
            return False
        # 获取safeid
        safeid_pattern = r'&safeid=([^"]+)"'
        match_safeid = re.findall(safeid_pattern, res)
        if not match_safeid:
            return False
        self.user_setting["safeid"] = match_safeid[0]
        # 获取用户名
        username_pattern = r'placeholder="([^"]+)'
        match_username = re.findall(username_pattern, res)
        if not match_username:
            return False
        self.user_setting["username"] = match_username[0]
        return True

    def get_display_name(self):
        if self.user_setting.get("username"):
            return self.user_setting["username"]
        config_path = self.user_setting.get("_config_path")
        if config_path:
            return config_path.rsplit("\\", 1)[-1].rsplit("/", 1)[-1]
        return "未命名账号"

    def persist_cookie(self, stage: str):
        cookie_value = request.serialize_cookies(self.client)
        if not cookie_value:
            return False

        if cookie_value == self.user_setting.get("cookie", ""):
            return False

        self.user_setting["cookie"] = cookie_value
        changed = config.write_cookie(self.user_setting.get("_config_path", ""), cookie_value)
        if changed:
            print(self.get_display_name() + f" {stage}后已回写最新 cookie")
        return changed
