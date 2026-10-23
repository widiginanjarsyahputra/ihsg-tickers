# ihsg-tickers

Daftar saham IHSG yang aktif diperdagangkan (rata-rata nilai transaksi 20 hari ≥ Rp1 miliar), diperbarui otomatis setiap minggu (Sabtu 01:00 WIB) oleh GitHub Actions.

Dipakai sebagai cakupan screener di aplikasi **Jurnal IDX**.

| File | Isi |
|---|---|
| `ihsg_tickers.csv` | Daftar kode saham (format `KODE.JK`) + jumlah saham beredar (`Shares`, untuk market cap) |
| `meta.json` | Tanggal pembaruan, jumlah saham, status |
| `update_tickers.py` | Script penyaring (sumber daftar emiten: Wikipedia, data harga: Yahoo Finance) |
| `.github/workflows/update_list.yml` | Jadwal: setiap Sabtu 01:00 WIB, bisa juga dijalankan manual dari tab Actions |

Jika hasil penyaringan kurang dari 100 saham (misalnya sumber data sedang bermasalah), daftar lama dipertahankan.

Bukan rekomendasi investasi.

## Aturan ARA/ARB (`aturan.json`)
Batas auto rejection BEI per periode, dipakai aplikasi Jurnal Saham untuk validasi harga. Bila BEI mengubah aturan, cukup tambahkan periode baru di file ini; aplikasi mengambilnya otomatis tanpa instal ulang.
