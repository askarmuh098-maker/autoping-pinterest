import os
import requests
import json
from bs4 import BeautifulSoup

def get_blog_data(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Mengambil Judul (dari tag <title> atau og:title)
        title = soup.find("meta", property="og:title")
        title = title["content"] if title else soup.title.string
        
        # Mengambil Gambar (dari og:image yang biasanya gambar utama blog)
        image = soup.find("meta", property="og:image")
        image_url = image["content"] if image else ""
        
        return title.strip(), image_url.strip()
    except Exception as e:
        print(f"⚠️ Gagal mengambil data dari {url}: {e}")
        return None, None

def create_pin(token, board_id, image_url, title, link):
    api_url = "https://api.pinterest.com/v5/pins"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "board_id": board_id,
        "media_source": {
            "source_type": "image_url",
            "url": image_url
        },
        "title": title,
        "link": link
    }
    response = requests.post(api_url, headers=headers, json=payload)
    return response.json()

def main():
    token = os.environ.get('AMASRXAXAC2CWAQAGBAKQDE3FOQK3HIBQBIQD275WNP625XRZ456HX5W2RBJYR7BI5ZKYJRZ4VB5TE4AXQEMTX5T4Z2O3UIA')
    board_id = "912049362503607035" # Ganti dengan Board ID Bapak
    
    if not os.path.exists('pins.txt'):
        print("File pins.txt tidak ada!")
        return

    with open('pins.txt', 'r') as f:
        urls = [line.strip() for line in f.readlines() if line.strip()]

    if not urls:
        print("Daftar URL di pins.txt kosong!")
        return

    # Ambil 10 URL pertama
    target_urls = urls[:10]
    remaining_urls = urls[10:] + target_urls

    for url in target_urls:
        title, img = get_blog_data(url)
        
        if title and img:
            print(f"📸 Memproses: {title}")
            res = create_pin(token, board_id, img, title, url)
            print(f"📥 Respon Pinterest: {res}")
        else:
            print(f"⏭️ Melewati {url} karena data tidak lengkap.")

    # Simpan kembali rotasi URL
    with open('pins.txt', 'w') as f:
        f.write('\n'.join(remaining_urls))

if __name__ == "__main__":
    main()
