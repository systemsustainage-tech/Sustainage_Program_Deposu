import sys
from typing import Dict, Optional, Tuple

import requests


def _extract_csrf(html: str) -> Optional[str]:
    marker = 'name="csrf_token"'
    idx = html.find(marker)
    if idx == -1:
        return None
    sub = html[idx : idx + 500]
    vmarker = 'value="'
    vidx = sub.find(vmarker)
    if vidx == -1:
        return None
    rest = sub[vidx + len(vmarker) :]
    return rest.split('"', 1)[0] if '"' in rest else None


def _captcha_needed(html: str) -> bool:
    return 'name="captcha"' in (html or "")


def _solve_captcha(question: str) -> Optional[str]:
    q = (question or "").strip()
    tokens = q.replace("=", " ").replace("?", " ").split()
    if len(tokens) < 3:
        return None
    try:
        a = float(tokens[0].replace(",", "."))
        op = tokens[1]
        b = float(tokens[2].replace(",", "."))
    except Exception:
        return None

    if op == "+":
        return str(int(a + b)) if float(a + b).is_integer() else str(a + b)
    if op == "-":
        return str(int(a - b)) if float(a - b).is_integer() else str(a - b)
    if op in ("*", "x", "X"):
        return str(int(a * b)) if float(a * b).is_integer() else str(a * b)
    if op == "/":
        if b == 0:
            return None
        val = a / b
        return str(int(val)) if float(val).is_integer() else str(val)
    return None


def login(session: requests.Session, base_url: str, username: str, password: str) -> Tuple[bool, Dict]:
    login_url = f"{base_url}/login"
    r = session.get(login_url, timeout=20, verify=False)
    csrf = _extract_csrf(r.text or "")
    need_captcha = _captcha_needed(r.text or "")

    data = {"username": username, "password": password}
    if csrf:
        data["csrf_token"] = csrf
    if need_captcha:
        cap = session.get(f"{base_url}/captcha_image", timeout=20, verify=False)
        try:
            payload = cap.json()
        except Exception:
            payload = {}
        answer = _solve_captcha(str(payload.get("question", "")))
        if answer is not None:
            data["captcha"] = answer

    pr = session.post(login_url, data=data, allow_redirects=True, timeout=20, verify=False)
    ok = (pr.status_code == 200) and ("/login" not in (pr.url or "")) and ("Kullanıcı adı veya parola hatalı" not in (pr.text or ""))
    return ok, {"final_url": pr.url, "status": pr.status_code}


def main() -> int:
    base_url = "https://sustainage.cloud"
    username = "__super__"
    password = "Su5t@inage-Temp-6Kp9V2!"
    if len(sys.argv) > 1:
        username = sys.argv[1].strip()
    if len(sys.argv) > 2:
        password = sys.argv[2]

    s = requests.Session()
    ok, info = login(s, base_url, username, password)
    print("login_ok:", ok, info)

    paths = ["/social", "/supply_chain", "/governance", "/cdp"]
    for p in paths:
        r = s.get(f"{base_url}{p}", allow_redirects=False, timeout=20, verify=False)
        print(p, r.status_code, r.headers.get("Location", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
