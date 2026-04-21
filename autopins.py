import os
import requests
import json
from bs4 import BeautifulSoup
import time

# --- KONFIGURASI ---
# Ganti angka di bawah ini dengan ID Papan Pinterest Bapak (18 Angka)
BOARD_ID = "912049362503607035" 

def get_blog_data(url):
    """Mengambil Judul dan Gambar otomatis dari blog"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ambil Judul
        title_tag = soup.find("meta", property="og:title")
        title = title_tag["content"] if title_tag else (soup.title.string if soup.title else "Artikel Tips News")
        
        # Ambil Gambar Utama
        image_url = ""
        image_tag = soup.find("meta", property="og:image")
        if image_tag:
            image_url = image_tag["content"]
        
        # Jika og:image tidak ada, cari gambar pertama di artikel
        if not image_url:
            post_content = soup.find('div', class_='post-body') or soup.find('article')
            if post_content:
                img_tag = post_content.find('img')
                if img_tag:
                    image_url = img_tag.get('src') or img_tag.get('data-src')

        return title.strip(), image_url.strip() if image_url else None
    except Exception as e:
        print(f"⚠️ Gagal mengambil data blog {url}: {e}")
        return None, None

def create_pin(token, board_id, image_url, title, link):
    """Mengirim Pin ke Pinterest API v5"""
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
        "title": title[:99],
        "description": "Informasi terbaru dari Tips News Eu Org.",
        "link": link
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        return {"status": "failure", "message": str(e)}

def main():
    # MENGAMBIL TOKEN DARI GITHUB SECRETS (Paling Aman)
    # Pastikan di GitHub Secrets Bapak sudah ada nama 'PINTEREST_TOKEN'
    token = os.environ.get('PINTEREST_TOKEN')
    
    if not token:
        print("❌ Error: PINTEREST_TOKEN tidak ditemukan di GitHub Secrets!")
        return

    if not os.path.exists('pins.txt'):
        print("❌ Error: File pins.txt tidak ditemukan!")
        return

    # Baca daftar URL
    with open('pins.txt', 'r') as f:
        urls = [line.strip() for line in f.readlines() if line.strip()]

    if not urls:
        print("⚠️ pins.txt kosong.")
        return

    # Proses 10 Pin per hari
    target_urls = urls[:10]
    # Pindahkan 10 link tersebut ke urutan paling bawah
    new_list = urls[10:] + target_urls

    print(f"🚀 Memulai posting {len(target_urls)} Pin...")

    berhasil = 0
    for url in target_urls:
        title, img = get_blog_data(url)
        
        if title and img:
            res = create_pin(token, BOARD_ID, img, title, url)
            if 'id' in res:
                print(f"✅ BERHASIL: {title}")
                berhasil += 1
                time.sleep(10) # Jeda 10 detik agar aman
            else:
                print(f"❌ GAGAL {url}: {res.get('message', 'Cek Token/ID Papan')}")
        else:
            print(f"⏭️ SKIP: {url} (Gambar tidak ditemukan)")

    # Simpan kembali daftar yang sudah diputar urutannya
    with open('pins.txt', 'w') as f:
        f.write('\n'.join(new_list))
    
    print(f"\nSelesai! {berhasil} Pin sukses dibuat hari ini.")

if __name__ == "__main__":
    main()
