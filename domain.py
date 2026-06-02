import os
import re
import requests
from collections import defaultdict
from random import choice
from urllib.parse import urlparse

BASE_DIR = "./"

DOMAIN_REGEX = r"https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"

domain_sources = defaultdict(set)
seen_domains = set()

# Proxy kaynakları (GitHub raw)
PROXY_URLS = [
    "https://raw.githubusercontent.com/opitiopiti/yenisistem/refs/heads/main/dizipod/pro.txt",
    "https://raw.githubusercontent.com/opitiopiti/yenisistem/refs/heads/main/sinewix/pro.txt"
]

# Proxyleri çek
proxies_list = []

for url in PROXY_URLS:
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()

        # satır satır proxy
        proxies_list.extend([
            line.strip()
            for line in r.text.splitlines()
            if line.strip()
        ])

    except Exception as e:
        print(f"Proxy fetch error: {url} -> {e}")

print(f"[INFO] Loaded {len(proxies_list)} proxies")


def extract_domains(text):
    return re.findall(DOMAIN_REGEX, text)


def try_request(url, proxies=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        if proxies:
            r = requests.get(
                url,
                headers=headers,
                timeout=10,
                proxies=proxies,
                allow_redirects=True
            )
        else:
            r = requests.get(
                url,
                headers=headers,
                timeout=10,
                allow_redirects=True
            )

        final_url = r.url
        final_domain = urlparse(final_url).netloc

        return r.status_code, final_domain

    except:
        return None, None


def get_with_proxies(domain):
    url = f"http://{domain}"

    # 1) normal dene
    status, final_domain = try_request(url)

    if status and status != 403:
        return status, final_domain

    print(f"[403/ERROR] {url} -> proxy denenecek")

    # 2) proxy dene
    for _ in range(len(proxies_list)):
        proxy = choice(proxies_list)

        proxy_dict = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }

        status, final_domain = try_request(url, proxies=proxy_dict)

        if status and status != 403:
            return status, final_domain

    return None, None


def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    domains = extract_domains(content)

    for domain in domains:

        status, final_domain = get_with_proxies(domain)

        if status:
            print(f"[OK] {domain} -> {status} (final: {final_domain})")
        else:
            print(f"[FAILED] {domain}")

        if domain not in seen_domains:
            seen_domains.add(domain)

        domain_sources[domain].add(file_path)


def scan_repo(base_dir):
    for file in os.listdir(base_dir):
        if file.endswith(".txt"):
            full_path = os.path.join(base_dir, file)
            print(f"\nProcessing: {full_path}")
            process_file(full_path)


if __name__ == "__main__":
    scan_repo(BASE_DIR)

    print("\n=== DOMAIN REPORT ===")
    for domain, sources in domain_sources.items():
        print(f"{domain} -> {list(sources)}")
