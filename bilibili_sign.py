"""Bilibili live activity check-in using your own authorized cookie.

Required environment variables:
    BILI_COOKIE, BILI_ACTIVITY_ID, BILI_RUIDS
"""
import os
import sys
import time
from datetime import date, timedelta

import requests

API = "https://api.live.bilibili.com/xlive/custom-activity-interface/baseActivity"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36",
    "Referer": "https://live.bilibili.com/",
}


def call(session, method, endpoint, **kwargs):
    response = session.request(method, endpoint, timeout=20, **kwargs)
    response.raise_for_status()
    result = response.json()
    if result.get("code") != 0:
        raise RuntimeError(f"code={result.get('code')}, message={result.get('message')}")
    return result.get("data")


def main():
    cookie = os.environ.get("BILI_COOKIE", "").strip()
    activity = os.environ.get("BILI_ACTIVITY_ID", "").strip()
    uids = [item.strip() for item in os.environ.get("BILI_RUIDS", "").split(",") if item.strip()]
    if not cookie or not activity or not uids:
        print("配置缺失：请设置 BILI_COOKIE、BILI_ACTIVITY_ID、BILI_RUIDS 环境变量。")
        return 2
    if not activity.isdigit() or any(not uid.isdigit() for uid in uids):
        print("活动 ID 和主播 UID 必须为数字。")
        return 2

    cookies = dict(part.strip().split("=", 1) for part in cookie.split(";") if "=" in part)
    csrf = cookies.get("bili_jct", "").strip()
    if not csrf or not cookies.get("SESSDATA"):
        print("Cookie 必须包含有效的 SESSDATA 和 bili_jct。")
        return 2

    session = requests.Session()
    session.headers.update(HEADERS)
    session.headers["Cookie"] = cookie
    try:
        nav = call(session, "GET", "https://api.bilibili.com/x/web-interface/nav")
        if not isinstance(nav, dict) or not nav.get("isLogin"):
            print("登录状态无效，请更新 Cookie。")
            return 1
        print(f"登录成功：{nav.get('uname', '未知用户')}")
    except (requests.RequestException, ValueError, RuntimeError) as ex:
        print(f"登录验证失败：{ex}")
        return 1

    today = date.today()
    month_end = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    failed = 0
    for uid in dict.fromkeys(uids):
        try:
            info = call(session, "GET", API + "/ListSignInInfo", params={
                "activity_id": activity,
                "csrf": csrf,
                "start_date": today.isoformat(),
                "end_date": month_end.isoformat(),
                "ruid": uid,
            })
            if not isinstance(info, dict):
                raise RuntimeError("活动未返回有效签到信息，可能已过期")
            if not info.get("is_fans"):
                print(f"主播 {uid}：不符合粉丝资格或活动未开放，跳过")
                continue
            if info.get("is_sign_in_today"):
                print(f"主播 {uid}：今日已签到")
                continue
            call(session, "POST", API + "/DoSignIn", params={
                "access_key": "",
                "activity_id": activity,
                "brand": "",
                "build": "",
                "channel": "",
                "csrf": csrf,
                "ruid": uid,
                "platform": "web",
            })
            print(f"主播 {uid}：签到请求成功（请按活动页面核实奖励）")
        except (requests.RequestException, ValueError, RuntimeError) as ex:
            print(f"主播 {uid}：签到失败：{ex}")
            failed += 1
        time.sleep(1)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
