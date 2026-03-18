import re
import sys
from urllib.parse import urljoin

import requests


def main() -> int:
    base_url = "https://sustainage.cloud"
    login_url = urljoin(base_url, "/login")

    username = "__super__"
    password = "Su5t@inage-Temp-6Kp9V2!"

    if len(sys.argv) > 1:
        username = sys.argv[1].strip()
    if len(sys.argv) > 2:
        password = sys.argv[2]

    s = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    r = s.get(login_url, headers=headers, timeout=20)
    csrf = None
    if r.status_code == 200:
        m = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', r.text)
        if m:
            csrf = m.group(1)

    data = {"username": username, "password": password}
    if csrf:
        data["csrf_token"] = csrf

    headers_post = dict(headers)
    headers_post["Referer"] = login_url
    headers_post["Origin"] = base_url
    pr = s.post(login_url, data=data, headers=headers_post, allow_redirects=True, timeout=20)

    text = pr.text or ""
    invalid = "Kullanıcı adı veya parola hatalı" in text
    captcha = ("Güvenlik kodu hatalı" in text) or ("Güvenlik doğrulaması başarısız" in text)
    rate_limited = pr.status_code == 429 or "Too Many Requests" in text

    print("GET /login:", r.status_code, "csrf_token:", bool(csrf))
    print("POST /login:", pr.status_code, "final_url:", pr.url)
    print("flags:", {"invalid_credentials_msg": invalid, "captcha_msg": captcha, "rate_limited": rate_limited})

    if pr.status_code in (301, 302, 303, 307, 308):
        return 1
    if pr.status_code >= 400:
        return 1
    if "/dashboard" in pr.url:
        return 0
    if "Giriş başarılı" in text:
        return 0
    if invalid or captcha or rate_limited:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
