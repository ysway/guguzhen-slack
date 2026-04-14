import re

from bs4 import BeautifulSoup

from src.utils import request


class Clip(object):

    def __init__(self, user_setting: dict, client):
        self.client = client
        self.user_setting = user_setting
        self.param = {
            "safeid": user_setting["safeid"],
            "c": "8",
            "id": 0
        }
        self.headers = request.build_headers(form=True)
        self.url = "https://www.momozhen.com/fyg_click.php"
        self.clip_setting = max(-1, min(user_setting["fight"]["flip_card_mode"], 1))
        self.perspective_list = []
        self.position_map = {
            1: "舞",
            2: "默",
            3: "琳",
            4: "艾",
            5: "梦",
            6: "薇",
            7: "伊",
            8: "冥",
            9: "命",
            10: "希",
            11: "霞",
            12: "绮"
        }
        self.clip_info = {
            "幸运": 0,
            "稀有": 0,
            "史诗": 0,
            "传说": 0
        }

    def run(self):
        print(self.user_setting["username"] + " 开始翻牌...")
        refresh_res = self.refresh()
        if not refresh_res:
            return

        if self.perspective_list:
            print(self.user_setting["username"] + " 获取到透视：" + ",".join(self.perspective_list))
            for perspective_index, perspective_card in enumerate(self.perspective_list, start=1):
                if perspective_card == "传说":
                    self.param["id"] = perspective_index
                    self.flip_cards(loop=False)

        self.param["id"] = len(self.perspective_list) + 1
        self.flip_cards()

    def refresh(self):
        url = "https://www.momozhen.com/fyg_read.php"
        param = {
            "f": "10"
        }
        res = request.post_data(url, self.headers, param, self.client)
        if not res or not res.startswith('<div class="row fyg_tc">'):
            print(res)
            print(self.user_setting["username"] + " 结束翻牌")
            return False

        self.load_perspective(res)
        if not self.analysis_clip_result(res):
            print(self.user_setting["username"] + " 翻牌结果解析失败！结束翻牌")
            return False
        return self.print_clip_summary()

    def load_perspective(self, res: str):
        pattern = r'是“(.*?)”</p>'
        matches = re.findall(pattern, res)
        if matches:
            self.perspective_list = matches[0].split(",")
            return
        self.perspective_list = []
        self.clip_setting = -1

    def print_clip_summary(self):
        print_info = self.user_setting["username"]
        for key, value in self.clip_info.items():
            print_info += f" {key}：{value}"
            if value > 2:
                print(f"{self.user_setting['username']} 翻牌结束！结果：{key}")
                return False
        print(print_info)
        return True

    def analysis_clip_result(self, res: str):
        clip_dom = BeautifulSoup(res, "html.parser")
        read_list = []
        for button in clip_dom.find_all("button"):
            classes = button.get("class") or []
            if any("fyg_lh60" in class_name for class_name in classes):
                read_list.append(button.get_text(strip=True))

        if not read_list:
            return False

        self.clip_info = {
            "幸运": 0,
            "稀有": 0,
            "史诗": 0,
            "传说": 0
        }
        for item in read_list:
            if item in self.clip_info:
                self.clip_info[item] += 1
        return True

    def flip_cards(self, loop: bool = True):
        res = request.post_data(self.url, self.headers, self.param, self.client)
        if res is None:
            return

        if res == "" or res.startswith('<p class="fyg_f18">'):
            print(self.user_setting["username"] + " 已翻开：" + self.position_map.get(self.param["id"], str(self.param["id"])))
            refresh_res = self.refresh()
            if not refresh_res or not loop:
                return
            self.get_next_id()
            self.flip_cards()
            return

        if res == "该牌面已翻开":
            if loop:
                self.get_next_id()
                self.flip_cards()
            return

        print(res)

    def get_next_id(self):
        if self.has_double_legend():
            self.param["id"] += 1
            return

        if self.should_force_guarantee():
            self.flip_guarantee_card()
            return

        self.param["id"] += 1

    def has_double_legend(self):
        return self.clip_setting == 0 and self.clip_info["传说"] > 1

    def should_force_guarantee(self):
        return self.clip_setting in (0, 1) and self.clip_info["幸运"] > 1

    def flip_guarantee_card(self):
        guaranteed_key = self.get_guaranteed_key()
        if not guaranteed_key:
            self.param["id"] += 1
            return

        for perspective_index, perspective in enumerate(self.perspective_list, start=1):
            if perspective == guaranteed_key:
                self.param["id"] = perspective_index
                self.flip_cards(loop=False)
                return

        self.param["id"] += 1

    def get_guaranteed_key(self):
        merge_clip_info = dict(self.clip_info)
        for perspective in self.perspective_list:
            if perspective in merge_clip_info and perspective != "传说":
                merge_clip_info[perspective] += 1
        if merge_clip_info["史诗"] > 2:
            return "史诗"
        if merge_clip_info["稀有"] > 2:
            return "稀有"
        return ""

