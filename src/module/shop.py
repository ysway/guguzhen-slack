from src.utils import request, config


class Shop(object):

    def __init__(self, user_setting: dict, client):
        self.client = client
        self.user_setting = user_setting
        self.shop_setting = user_setting["shop"]
        self.param = {
            "safeid": user_setting["safeid"],
            "c": ""
        }
        self.headers = request.build_headers(form=True)
        self.url = "https://www.momozhen.com/fyg_shop_click.php"

    def run(self):
        # bvip日活
        print(self.user_setting["username"] + " 开始领取BVIP打卡包...")
        self.param["c"] = "11"
        bvip_res = request.post_data(self.url, self.headers, self.param, self.client)
        print(config.format_html(bvip_res))
        # svip日活
        print(self.user_setting["username"] + " 开始领取SVIP打卡包...")
        self.param["c"] = "12"
        svip_res = request.post_data(self.url, self.headers, self.param, self.client)
        print(config.format_html(svip_res))
        if self.shop_setting["sand_to_shell"]:
            # 星沙日活
            print(self.user_setting["username"] + " 开始1星沙兑换10w贝壳...")
            self.param["c"] = "5"
            res = request.post_data(self.url, self.headers, self.param, self.client)
            print(config.format_html(res))
        if self.shop_setting["crystal_to_shell"]:
            # 星晶日活
            print(self.user_setting["username"] + " 开始1星晶兑换120w贝壳...")
            self.param["c"] = "6"
            res = request.post_data(self.url, self.headers, self.param, self.client)
            print(config.format_html(res))
        if self.shop_setting["sand_to_potion"]:
            # 买药水
            self.buy_potion()

    def buy_potion(self):
        print(self.user_setting["username"] + " 开始购买药水...")
        self.param["c"] = "7"
        res = request.post_data(self.url, self.headers, self.param, self.client)
        print(config.format_html(res))
        if res and "已获得 体能刺激药水" in res:
            self.buy_potion()
