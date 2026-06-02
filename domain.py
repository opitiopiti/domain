import os
import re
import requests
from collections import defaultdict
from random import choice

BASE_DIR = "./"  # Ana dizin

DOMAIN_REGEX = r"https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"

domain_sources = defaultdict(set)
seen_domains = set()

# Proxy raw dosyaları
PROXY_URLS = [
    "https://raw.githubusercontent.com/opitiopiti/yenisistem/refs/heads/main/dizipod/pro.txt",
    "https://raw.githubusercontent.com/opitiopiti/yenisistem/refs/heads/main/sinewix/pro.txt"
]

# Proxyleri çek
proxies_list = []
for url in PROXY_URLS:
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        proxies_list.extend([line.strip() for line in r.text.split() if line.strip()])
    except Exception as e:
        print(f"Proxy fetch error from {url}: {e}")

print(f"Loaded {len(proxies_list)} proxies.")


def extract_domains(text):
    return re.findall(DOMAIN_REGEX, text)


def get_with_proxies(domain):
    url = f"http://{domain}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    # Önce normal istek
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code != 403:
            return r.status_code
        print(f"[403] {url} -> Trying proxies...")
    except:
        print(f"[ERROR] {url} -> Trying proxies...")

    # Proxy ile deneme
    for _ in range(len(proxies_list)):
        proxy = choice(proxies_list)
        proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        try:
            r = requests.get(url, headers=headers, proxies=proxy_dict, timeout=5)
            if r.status_code != 403:
                return r.status_code
        except:
            continue
    return None


def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    domains = extract_domains(content)

    for domain in domains:
        status = get_with_proxies(domain)
        if status:
            print(f"[OK] http://{domain} -> {status}")
        else:
            print(f"[FAILED] http://{domain}")

        if domain not in seen_domains:
            seen_domains.add(domain)
        domain_sources[domain].add(file_path)


def scan_repo(base_dir):
    for file in os.listdir(base_dir):
        if file.endswith(".txt"):
            full_path = os.path.join(base_dir, file)
            print(f"Processing: {full_path}")
            process_file(full_path)


if __name__ == "__main__":
    scan_repo(BASE_DIR)

    print("\n=== DOMAIN REPORT ===")
    for domain, sources in domain_sources.items():
        print(f"{domain} -> {list(sources)}")
