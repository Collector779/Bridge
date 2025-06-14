import time
import requests
import random
import html

URL = "https://bridges.torproject.org/bridges?transport=obfs4"
PROXY_LIST_URL = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=https&timeout=500&country=all&ssl=all&anonymity=all"
PLIK_WYJSCIA = "gotowemostki.txt"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 Chrome/91.0.4472.120 Mobile Safari/537.36"
]

ACCEPT_HEADERS = [
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "text/html,application/xml;q=0.9,*/*;q=0.8",
    "text/html;q=0.9,image/avif,image/webp,*/*;q=0.8"
]

LANG_HEADERS = [
    "en-US,en;q=0.5",
    "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
    "en;q=0.8",
    "fr-FR,fr;q=0.9,en;q=0.8"
]

def losowy_user_agent():
    return random.choice(USER_AGENTS)

def losowe_naglowki():
    headers = {
        "User-Agent": losowy_user_agent(),
        "Accept": random.choice(ACCEPT_HEADERS),
        "Accept-Language": random.choice(LANG_HEADERS),
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    return dict(random.sample(list(headers.items()), len(headers)))

def pobierz_losowe_proxy():
    try:
        resp = requests.get(PROXY_LIST_URL, timeout=45)
        proxy_list = resp.text.strip().split('\n')
        proxy_list = [p.strip() for p in proxy_list if p.strip()]
        if not proxy_list:
            print("[!] Lista proxy pusta.")
            return None
        proxy = random.choice(proxy_list)
        return {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        }
    except Exception as e:
        print(f"[!] Błąd przy pobieraniu proxy: {e}")
        return None

def pobierz_mostki(proxy=None):
    session = requests.Session()
    try:
        headers = losowe_naglowki()
        session.headers.update(headers)
        response = session.get(URL, proxies=proxy, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"[!] Błąd przy połączeniu ({proxy}): {e}")
        return [], []

    text = response.text
    idx = text.find("Here are your bridge lines:")
    if idx == -1:
        return [], []

    fragment = text[idx:idx+2000]
    wszystkie_mostki = []
    iat2_mostki = []

    for line in fragment.splitlines():
        line = html.unescape(line.strip())
        if line.startswith("obfs4"):
            wszystkie_mostki.append(line)
            if "iat-mode=2" in line:
                iat2_mostki.append(line)

    return iat2_mostki, wszystkie_mostki

def zapisz_do_pliku(mostki):
    try:
        with open(PLIK_WYJSCIA, "a", encoding="utf-8") as f:
            for m in mostki:
                f.write(m + "\n")
        print(f"[💾] Zapisano {len(mostki)} mostek/mostki do pliku.")
        for m in mostki:
            print("   ", m)
    except Exception as e:
        print(f"[!] Błąd przy zapisie do pliku: {e}")

def main():
    while True:
        print("[🔄] Sprawdzam nowe mostki z losowym proxy i losowymi nagłówkami...")

        proxy = pobierz_losowe_proxy()
        if proxy is None:
            print("[!] Brak działającego proxy. Czekam 20 sekund...\n")
            time.sleep(20)
            continue

        iat2, wszystkie = pobierz_mostki(proxy=proxy)

        if iat2:
            print(f"[✔] Znaleziono {len(iat2)} mostek/mostki z iat-mode=2:")
            zapisz_do_pliku(iat2)
        elif wszystkie:
            print("[~] Nie znaleziono mostków z iat-mode=2, ale znaleziono inne obfs4:")
            for m in wszystkie:
                print("   ", m)
        else:
            print("[✘] Nie znaleziono żadnych mostków obfs4.")

        sleep_time = random.uniform(2, 8)
        print(f"[⏳] Czekam {round(sleep_time,1)} sek...\n")
        time.sleep(sleep_time)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Przerwano ręcznie. Kończę działanie.")