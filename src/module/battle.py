import re

from bs4 import BeautifulSoup

from src.module.clip import Clip
from src.utils import config, request


class Battle(object):

    def __init__(self, user_setting: dict, client):
        self.client = client
        self.user_setting = user_setting
        self.param = {
            "safeid": user_setting["safeid"],
            "id": ""
        }
        self.headers = request.build_headers(form=True)
        self.url = "https://www.momozhen.com/fyg_v_intel.php"
        self.battle_mode = max(0, min(user_setting["fight"]["battle_mode"], 4))
        self.potion_count = max(0, min(user_setting["fight"]["use_potion"], 2))
        self.dog_card = 0
        self.rank = ""

    def run(self):
        if self.battle_mode == 0:
            return

        self.get_rank()
        if not self.should_stop_battle():
            if self.battle_mode in (1, 3):
                self.param["id"] = "1"
                print(self.user_setting["username"] + " 开始打野...")
                self.run_battle_cycle()

            if self.battle_mode in (2, 4):
                self.param["id"] = "2"
                print(self.user_setting["username"] + " 开始打人...")
                self.run_battle_cycle()

        self.handle_rewards()
        self.try_use_potion()

    def run_battle_cycle(self):
        if self.should_stop_battle():
            return

        self.get_rank()
        res = request.post_data(self.url, self.headers, self.param, self.client)
        if res and res.startswith('<div class="row">'):
            self.print_battle_result(res)
            self.get_rank()
            self.run_battle_cycle()
            return

        if res and "请重试" in res:
            print(config.format_html(res))
            self.run_battle_cycle()
            return

        print(config.format_html(res))
        print(self.user_setting["username"] + " 结束战斗")
        self.get_rank()

    def should_stop_battle(self):
        return self.battle_mode in (3, 4) and self.dog_card > 2

    def handle_rewards(self):
        if self.dog_card > 2:
            Clip(self.user_setting, self.client).run()
            return
        print(self.user_setting["username"] + " 狗牌不足！")

    def try_use_potion(self):
        if self.potion_count <= 0:
            return
        if not self.use_potion():
            return
        self.potion_count -= 1
        self.run()

    def use_potion(self):
        print(self.user_setting["username"] + " 消耗两瓶药水恢复体力...")
        param = {
            "safeid": self.user_setting["safeid"],
            "c": "13",
            "id": "2"
        }
        url = "https://www.momozhen.com/fyg_click.php"
        res = request.post_data(url, self.headers, param, self.client)
        print(config.format_html(res))
        return bool(res and res.startswith("可出击数已刷新"))

    def print_battle_result(self, res: str):
        user_name = self.user_setting["username"]
        enemy_name = self.get_enemy_name(res)
        if user_name + " 获得了胜利！" in res:
            print(user_name + " 赢了 " + enemy_name)
            return
        if "双方同归于尽！本场不计入胜负场次" in res:
            print(user_name + " 平了 " + enemy_name)
            return
        print(user_name + " 输了 " + enemy_name)

    def get_rank(self):
        url = "https://www.momozhen.com/fyg_read.php"
        param = {
            "f": "12"
        }
        res = request.post_data(url, self.headers, param, self.client)
        if not res:
            return

        rank_pattern = r'font-weight:900;">(.*?)</span><br>当前所在段位'
        rank_matches = re.findall(rank_pattern, res)
        if rank_matches:
            self.rank = rank_matches[0]

        dog_pattern = r'font-weight:700;">(.*?)</span><br>今日获得狗牌'
        dog_matches = re.findall(dog_pattern, res)
        if dog_matches:
            self.dog_card = int(dog_matches[0].split(" /")[0])

    @staticmethod
    def get_enemy_name(res: str):
        battle_soup = BeautifulSoup(res, "html.parser")
        for text in battle_soup.stripped_strings:
            match = re.match(r'^(.*?)（(.*?) Lv\.(\d+)）$', text)
            if match:
                return match.group(1)
        return "未知对手"
