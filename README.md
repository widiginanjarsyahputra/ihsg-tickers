# ihsg-tickers

Daftar saham IHSG yang aktif diperdagangkan (rata-rata nilai transaksi 20 hari ≥ Rp1 miliar), diperbarui otomatis setiap bulan oleh GitHub Actions.

Dipakai sebagai cakupan screener di aplikasi **Jurnal IDX**.

| File | Isi |
|---|---|
| `ihsg_tickers.csv` | Daftar kode saham (format `KODE.JK`) |
| `meta.json` | Tanggal pembaruan, jumlah saham, status |
| `update_tickers.py` | Script penyaring (sumber daftar emiten: Wikipedia, data harga: Yahoo Finance) |
| `.github/workflows/update_list.yml` | Jadwal: tanggal 1 setiap bulan, bisa juga dijalankan manual dari tab Actions |

Jika hasil penyaringan kurang dari 100 saham (misalnya sumber data sedang bermasalah), daftar lama dipertahankan.

Bukan rekomendasi investasi.
