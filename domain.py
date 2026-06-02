import os
import re
import requests
from collections import defaultdict

# Ana dizin (GitHub'dan clone edilmiş repo klasörü)
BASE_DIR = "./"  # Ana dizin

# Domain regex
DOMAIN_REGEX = r"https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"

# Her domain hangi dosyadan geldi
domain_sources = defaultdict(set)

# Daha önce görülen domainler
seen_domains = set()


def extract_domains(text):
    return re.findall(DOMAIN_REGEX, text)


def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    domains = extract_domains(content)

    for domain in domains:
        # GET isteği at
        try:
            url = f"http://{domain}"
            response = requests.get(url, timeout=5)
            print(f"[OK] {url} -> {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {url} -> {e}")

        # Domain yeni mi kontrol et
        if domain not in seen_domains:
            seen_domains.add(domain)
        domain_sources[domain].add(file_path)


def scan_repo(base_dir):
    # Ana dizindeki .txt dosyalarını al
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
