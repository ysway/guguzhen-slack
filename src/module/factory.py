import re

from src.utils import request, config


class Factory(object):

    def __init__(self, user_setting: dict, client):
        self.client = client
        self.user_setting = user_setting
        self.sand_threshold = user_setting["factory"]
        self.beach_setting = user_setting.get("beach", {})
        if self.sand_threshold > 10:
            self.sand_threshold = 10
        self.param = {
            "f": "21"
        }
        self.headers = request.build_headers(form=True)
        self.url = "https://www.momozhen.com/fyg_read.php"

    def run(self):
        should_clear_beach = self.beach_setting.get("clear_equipment", False)
        if self.sand_threshold <= 0 and not should_clear_beach:
            return
        # 刷新沙滩
        request.get("https://www.momozhen.com/fyg_beach.php", request.build_headers(), self.client)
        if should_clear_beach:
            self.clear_beach_equipment()
        # 获取星沙
        if self.sand_threshold <= 0:
            return
        res = request.post_data(self.url, self.headers, self.param, self.client)
        if not res:
            return
        pattern = r'已开采<br>(.*?)星沙'
        match = re.findall(pattern, res)
        if not match:
            return
        now_sand = int(match[0])
        # 判断收工
        if now_sand >= self.sand_threshold:
            print(self.user_setting["username"] + " 宝石工坊收工...")
            url = "https://www.momozhen.com/fyg_click.php"
            param = {
                "safeid": self.user_setting["safeid"],
                "c": "30"
            }
            complete_res = request.post_data(url, self.headers, param, self.client)
            print(config.format_html(complete_res))
            # 收完工立即开工
            if "收工统计" in complete_res:
                start_res = request.post_data(url, self.headers, param, self.client)
                print(config.format_html(start_res))
        else:
            print(
                f"{self.user_setting['username']} 宝石工坊已开采 {now_sand} 星沙，"
                f"未达到收工阈值 {self.sand_threshold}"
            )

    def clear_beach_equipment(self):
        print(self.user_setting["username"] + " 清理沙滩装备...")
        cleanup_url = "https://www.momozhen.com/fyg_click.php"
        cleanup_param = {
            "safeid": self.user_setting["safeid"],
            "c": "20"
        }
        request.post_data(cleanup_url, self.headers, cleanup_param, self.client)

        stall_param = {
            "f": "1"
        }
        request.post_data(self.url, self.headers, stall_param, self.client)
