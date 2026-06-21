#!/usr/bin/env python3
"""Avrasya Araştırmaları Bülteni - Günlük Otomatik Araştırma Script'i"""

import json
import requests
import hashlib
import re
from datetime import datetime

DATA_PATH = "data/yayinlar.json"

def yukle_yayinlar():
    """Mevcut yayınları JSON'dan yükler."""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def kaydet_yayinlar(yayinlar):
    """Yayınları JSON'a kaydeder."""
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(yayinlar, f, ensure_ascii=False, indent=4)

def hash_baslik(baslik):
    """Başlıktan kısa bir hash üretir (mükerrer kontrolü için)."""
    return hashlib.md5(baslik.strip().lower().encode()).hexdigest()[:8]

def mevcut_hashler(yayinlar):
    """Mevcut yayınların hash setini döndürür."""
    return {hash_baslik(y["baslik"]) for y in yayinlar}

def google_scholar_ara(query, max_results=3):
    """Google Scholar'da arama yapar (varsayılan)."""
    # Not: Google Scholar API'si kısıtlıdır. 
    # Gerçek üretimde SerpAPI veya Crossref API kullanılabilir.
    print(f"  [Scholar] Aranıyor: {query}")
    # Buraya gerçek API entegrasyonu gelecek
    return []

def crossref_ara(query, max_results=5):
    """CrossRef API üzerinden akademik yayın arar."""
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": max_results,
        "sort": "published",
        "order": "desc"
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        items = r.json().get("message", {}).get("items", [])
        sonuclar = []
        for item in items:
            baslik = ""
            if item.get("title"):
                baslik = item["title"][0]
            elif item.get("container-title"):
                baslik = item["container-title"][0]
            else:
                continue
            
            yazarlar = []
            for yazar in item.get("author", [])[:3]:
                ad = f"{yazar.get('given', '')} {yazar.get('family', '')}".strip()
                if ad:
                    yazarlar.append(ad)
            
            # DOI'den link oluştur
            doi = item.get("DOI", "")
            link = f"https://doi.org/{doi}" if doi else ""
            
            # Yıl
            tarih = str(item.get("published-print", {}).get("date-parts", [[None]])[0][0] or 
                       item.get("published-online", {}).get("date-parts", [[None]])[0][0] or "")
            
            # Dergi adı
            dergi = item.get("container-title", [""])[0] if item.get("container-title") else ""
            
            # Özet
            ozet = item.get("abstract", "")
            if ozet:
                ozet = re.sub(r'<[^>]+>', '', ozet)[:300]
            
            sonuclar.append({
                "baslik": baslik,
                "yazarlar": ", ".join(yazarlar) if yazarlar else "Çeşitli Yazarlar",
                "kaynak": "Crossref",
                "dergi": dergi,
                "ozet": ozet or "Bu çalışma hakkında özet bilgisi henüz eklenmemiştir.",
                "link": link,
                "tarih": tarih,
                "etiket": [query]
            })
        return sonuclar
    except Exception as e:
        print(f"  [Crossref] Hata: {e}")
        return []

def yeni_yayinlari_ekle(yayinlar, yeniler):
    """Mükerrer kontrolü yaparak yeni yayınları ekler."""
    mevcut = mevcut_hashler(yayinlar)
    max_id = max((y.get("id", 0) for y in yayinlar), default=0)
    eklenen = 0
    
    for y in yeniler:
        h = hash_baslik(y["baslik"])
        if h not in mevcut:
            max_id += 1
            y["id"] = max_id
            y["tur"] = "makale"
            yayinlar.insert(0, y)  # En üste ekle
            mevcut.add(h)
            eklenen += 1
            print(f"  ✓ Eklendi: {y['baslik'][:60]}...")
    
    return eklenen

def main():
    print("=" * 60)
    print("Avrasya Araştırmaları Bülteni - Günlük Tarama")
    print(f"Tarih: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    print("=" * 60)
    
    yayinlar = yukle_yayinlar()
    print(f"Mevcut yayın sayısı: {len(yayinlar)}")
    
    # Araştırma sorguları
    sorgular = [
        "Eurasian geopolitics Central Asia",
        "Eurasian Economic Union integration",
        "Silk Road Belt and Road Central Asia",
        "Eurasia security cooperation Russia China",
        "Turkey Eurasia foreign policy",
        "Caucasus regional dynamics geopolitics",
        "Shanghai Cooperation Organization",
        "Eurasian studies academic research"
    ]
    
    toplam_yeni = 0
    for sorgu in sorgular:
        print(f"\n🔍 Sorgu: '{sorgu}'")
        sonuclar = crossref_ara(sorgu, max_results=3)
        if sonuclar:
            eklenen = yeni_yayinlari_ekle(yayinlar, sonuclar)
            toplam_yeni += eklenen
            print(f"  -> {eklenen} yeni yayın eklendi")
    
    if toplam_yeni > 0:
        kaydet_yayinlar(yayinlar)
        print(f"\n✅ Toplam {toplam_yeni} yeni yayın eklendi.")
        print(f"📊 Güncel yayın sayısı: {len(yayinlar)}")
    else:
        print("\n📭 Yeni yayın bulunamadı.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
