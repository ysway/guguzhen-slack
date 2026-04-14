from src.utils import request, config


class Wish(object):

    def __init__(self, user_setting: dict, client):
        self.client = client
        self.user_setting = user_setting
        self.wish_setting = user_setting["wish"]
        self.param = {
            "safeid": user_setting["safeid"],
            "c": "18",
            "id": "10"
        }
        self.headers = request.build_headers(form=True)
        self.url = "https://www.momozhen.com/fyg_click.php"

    def run(self):
        if self.wish_setting:
            print(self.user_setting["username"] + " 开始许愿...")
            res = request.post_data(self.url, self.headers, self.param, self.client)
            print(config.format_html(res))
