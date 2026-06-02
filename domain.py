
import os
import re
import requests
from random import choice
from urllib.parse import urlparse

BASE_DIR = "./"

DOMAIN_REGEX = r"https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"

# Proxy kaynakları
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
        proxies_list.extend([line.strip() for line in r.text.splitlines() if line.strip()])
    except Exception as e:
        print(f"[Proxy fetch error] {url} -> {e}")

print(f"[INFO] Loaded {len(proxies_list)} proxies\n")

def extract_domains(text):
    return re.findall(DOMAIN_REGEX, text)

def try_request(url, proxies=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.google.com/"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10, proxies=proxies, allow_redirects=True)
        final_domain = urlparse(r.url).netloc
        return r.status_code, final_domain
    except:
        return None, None

def get_with_proxies(domain):
    url = f"https://{domain}"

    # normal dene
    status, final_domain = try_request(url)
    if status and status != 403:
        return status, final_domain

    print(f"[403/ERROR] {url} -> proxy denenecek")

    # proxy ile dene
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

def replace_domains_in_file(file_path, domain_map):
    """File içindeki tüm eski domainleri final domain ile değiştir"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    for old_domain, new_domain in domain_map.items():
        if old_domain != new_domain:
            content = re.sub(rf"https?://{re.escape(old_domain)}", f"https://{new_domain}", content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    domains = extract_domains(content)
    domain_map = {}

    for domain in domains:
        status, final_domain = get_with_proxies(domain)
        if status:
            print(f"[OK] {domain} -> {status} (final: {final_domain})")
            domain_map[domain] = final_domain
        else:
            print(f"[FAILED] {domain}")
            domain_map[domain] = domain  # başarısızsa değiştirme

    # Dosyayı final domainlere göre güncelle
    replace_domains_in_file(file_path, domain_map)

def scan_repo(base_dir):
    for file in os.listdir(base_dir):
        if file.endswith(".txt"):
            full_path = os.path.join(base_dir, file)
            print(f"\nProcessing: {full_path}")
            process_file(full_path)

if __name__ == "__main__":
    scan_repo(BASE_DIR)
    print("\n=== Tüm dosyalar güncellendi ===")
