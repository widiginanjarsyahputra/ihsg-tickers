import json
import time
from datetime import datetime, timezone
import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup

MIN_SAHAM = 100  # batas minimal hasil agar daftar lama ditimpa

# ==========================================
# LANGKAH 1: TARIK SEMUA EMITEN TERDAFTAR DI BEI
# ==========================================
def get_all_idx_tickers():
    print("🌐 [Langkah 1/2] Mengunduh seluruh daftar emiten resmi dari BEI...")
    tickers = set()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Sumber Utama: Wikipedia Daftar Perusahaan BEI
    wiki_urls = [
        "https://id.wikipedia.org/wiki/Daftar_perusahaan_yang_tercatat_di_Bursa_Efek_Indonesia",
        "https://en.wikipedia.org/wiki/List_of_companies_listed_on_the_Indonesia_Stock_Exchange"
    ]

    for url in wiki_urls:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                for td in soup.find_all(["td", "a", "th"]):
                    text = td.get_text().strip().upper()
                    if len(text) == 4 and text.isalpha():
                        tickers.add(f"{text}.JK")
        except Exception:
            pass

    # Sumber Sekunder: Dataset Publik GitHub
    if len(tickers) < 200:
        try:
            url = "https://raw.githubusercontent.com/datasets/indonesia-stock-exchange/master/data/stock_list.csv"
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                lines = res.text.split("\n")
                for line in lines[1:]:
                    parts = line.split(",")
                    if len(parts) > 0:
                        code = parts[0].replace('"', '').strip().upper()
                        if len(code) == 4 and code.isalpha():
                            tickers.add(f"{code}.JK")
        except Exception:
            pass

    # Fallback Darurat jika koneksi ke luar diblokir
    if not tickers:
        print("⚠️ Menggunakan daftar basis cadangan...")
        backup_list = [
            "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "BBNI.JK", "UNVR.JK",
            "ICBP.JK", "AMRT.JK", "BYAN.JK", "TPIA.JK", "BRPT.JK", "INDF.JK", "CPIN.JK",
            "KLBF.JK", "ADRO.JK", "PTBA.JK", "PGAS.JK", "ITMG.JK", "MEDC.JK", "AKRA.JK",
            "INKP.JK", "TKIM.JK", "GOTO.JK", "EMTK.JK", "SCMA.JK", "MIKA.JK", "HEAL.JK"
        ]
        tickers.update(backup_list)

    sorted_list = sorted(list(tickers))
    print(f"📋 Total {len(sorted_list)} emiten terdeteksi untuk diuji likuiditasnya.\n")
    return sorted_list


# ==========================================
# LANGKAH 2: FILTER LIKUIDITAS DENGAN YFINANCE (period="1mo")
# ==========================================
def update_ihsg_tickers():
    tickers = get_all_idx_tickers()
    
    print(f"🔍 [Langkah 2/2] Memeriksa likuiditas transaksi harian di Yahoo Finance...")
    
    active_tickers = []
    batch_size = 30  # Dipecah per 30 saham agar tidak kena limit Yahoo
    total_batches = (len(tickers) - 1) // batch_size + 1

    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]
        batch_num = i // batch_size + 1
        print(f"⏳ Memproses batch {batch_num}/{total_batches} ({len(batch)} saham)...")

        try:
            # Gunakan period="1mo" yang valid
            data = yf.download(tickers=batch, period="1mo", interval="1d", group_by="ticker", progress=False)
            if data.empty:
                continue

            for ticker in batch:
                try:
                    df = data[ticker].dropna() if len(batch) > 1 else data.dropna()
                    if df.empty or len(df) < 3:
                        continue

                    # Hitung Rata-rata Value Transaksi Harian (Close * Volume)
                    df['Value'] = df['Close'] * df['Volume']
                    avg_val = df['Value'].tail(20).mean()

                    # Saring saham dengan transaksi harian >= Rp 1 Milyar
                    if avg_val >= 1000_000_000:
                        active_tickers.append(ticker)
                except Exception:
                    continue

        except Exception as e:
            print(f"⚠️ Error pada batch {batch_num}: {e}")

        time.sleep(0.5)

    print(f"\n🎯 Hasil Pemindaian Total: Ditemukan {len(active_tickers)} saham aktif transaksi >= Rp 1 Milyar/hari.")

    # Pengaman: jangan timpa daftar lama jika hasil terlalu sedikit
    # (misalnya Yahoo Finance sedang bermasalah / sumber daftar emiten gagal diakses)
    if len(active_tickers) >= MIN_SAHAM:
        df_result = pd.DataFrame({"Ticker": sorted(active_tickers)})
        df_result.to_csv("ihsg_tickers.csv", index=False)
        print(f"💾 Berhasil menyimpan {len(active_tickers)} saham ke ihsg_tickers.csv!")
        status = "diperbarui"
    else:
        print(f"⚠️ Hanya {len(active_tickers)} saham lolos (< {MIN_SAHAM}). Daftar lama dipertahankan.")
        status = "dipertahankan"

    # Metadata untuk aplikasi Jurnal IDX (selalu ditulis agar jadwal bulanan tetap aktif)
    jumlah = len(pd.read_csv("ihsg_tickers.csv"))
    meta = {
        "diperbarui": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "jumlah": jumlah,
        "status": status,
        "filter": "Rata-rata nilai transaksi 20 hari >= Rp1 miliar",
    }
    with open("meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print(f"🗂️ meta.json: {meta}")

if __name__ == "__main__":
    update_ihsg_tickers()
