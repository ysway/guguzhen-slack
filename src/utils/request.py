import random
import time
from http.cookies import SimpleCookie

import httpx

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
)


def build_headers(form: bool = False):
    headers = {
        "user-agent": USER_AGENT,
    }
    if form:
        headers["content-type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    return headers


def create_client(cookie_value: str):
    client = httpx.Client(
        http2=True,
        verify=True,
        follow_redirects=True,
        timeout=10.0,
    )
    load_cookies(client, cookie_value)
    return client


def load_cookies(client: httpx.Client, cookie_value: str):
    if not cookie_value:
        return

    raw_cookie = SimpleCookie()
    try:
        raw_cookie.load(cookie_value)
    except Exception:
        raw_cookie = SimpleCookie()

    if raw_cookie:
        for morsel in raw_cookie.values():
            client.cookies.set(morsel.key, morsel.value, domain="www.momozhen.com", path="/")
        return

    for item in cookie_value.split(";"):
        cookie_part = item.strip()
        if not cookie_part or "=" not in cookie_part:
            continue
        name, value = cookie_part.split("=", 1)
        client.cookies.set(name.strip(), value.strip(), domain="www.momozhen.com", path="/")


def serialize_cookies(client: httpx.Client):
    return "; ".join(f"{name}={value}" for name, value in client.cookies.items())


def get(url: str, headers: dict, client: httpx.Client):
    try:
        response = client.get(url=url, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as error:
        print(f"{url} 请求失败！")
        print(error)
        return None


def post_data(url: str, headers: dict, data: dict, client: httpx.Client):
    time.sleep(random.random())
    try:
        response = client.post(url=url, headers=headers, data=data)
        response.raise_for_status()
        return response.text
    except Exception as error:
        print(f"{url} 请求失败！")
        print(error)
        return None
