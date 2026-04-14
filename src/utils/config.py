import os
from copy import deepcopy
from pathlib import Path

import yaml
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = {
    "cookie": "",
    "shop": {
        "sand_to_shell": False,
        "crystal_to_shell": False,
        "sand_to_potion": False,
    },
    "beach": {
        "clear_equipment": False,
    },
    "wish": False,
    "fight": {
        "battle_mode": 2,
        "flip_card_mode": 1,
        "use_potion": 0,
    },
    "factory": 3,
    "renew_key": True,
}


def get_config_dir():
    env_config_dir = os.environ.get("GUGUZHEN_CONFIG_DIR")
    candidate_paths = []
    if env_config_dir:
        candidate_paths.append(Path(env_config_dir).expanduser())

    candidate_paths.append(PROJECT_ROOT / "config")

    cwd_config_dir = Path.cwd() / "config"
    if cwd_config_dir not in candidate_paths:
        candidate_paths.append(cwd_config_dir)

    for candidate_path in candidate_paths:
        if candidate_path.exists():
            return candidate_path.resolve()

    return candidate_paths[0].resolve()


def _merge_config(default_value, user_value):
    if isinstance(default_value, dict):
        merged = {}
        user_value = user_value if isinstance(user_value, dict) else {}
        for key, nested_default in default_value.items():
            merged[key] = _merge_config(nested_default, user_value.get(key))
        for key, extra_value in user_value.items():
            if key not in merged:
                merged[key] = extra_value
        return merged
    if user_value is None:
        return deepcopy(default_value)
    return user_value


def read():
    config_dir = get_config_dir()
    if not config_dir.exists():
        print(f"未找到 config 文件夹，请将账号 yaml 配置放入 {config_dir}")
        return []

    config_data = []
    for file_path in sorted(config_dir.glob("*.yaml")):
        with file_path.open("r", encoding="utf-8") as file:
            setting = yaml.safe_load(file) or {}

        if not isinstance(setting, dict):
            print(f"{file_path.name} 不是有效的 yaml 配置，已跳过")
            continue

        merged_setting = _merge_config(DEFAULT_CONFIG, setting)
        merged_setting["_config_path"] = str(file_path)
        config_data.append(merged_setting)

    if not config_data:
        print(f"{config_dir} 中没有可用的 .yaml 配置")
    return config_data


def write_cookie(config_path: str, cookie_value: str):
    if not config_path:
        return False

    file_path = Path(config_path)
    if not file_path.exists():
        print(f"{file_path.name} 不存在，无法回写 cookie")
        return False

    with file_path.open("r", encoding="utf-8") as file:
        setting = yaml.safe_load(file) or {}

    if not isinstance(setting, dict):
        print(f"{file_path.name} 不是有效的 yaml 配置，无法回写 cookie")
        return False

    old_cookie = setting.get("cookie") or ""
    new_cookie = cookie_value or ""
    if old_cookie == new_cookie:
        return False

    setting["cookie"] = new_cookie
    with file_path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(setting, file, allow_unicode=True, sort_keys=False)

    print(f"{file_path.name} 已更新最新 cookie")
    return True


def format_html(text: str):
    if not text:
        return ""
    try:
        page_body = BeautifulSoup(text, "html.parser")
        content_list = list(page_body.stripped_strings)
        return " ".join(content_list) or text
    except Exception:
        return text
