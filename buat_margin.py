"""Buat margin.json dari lampiran Excel pengumuman BEI "Daftar Efek ... Transaksi Margin".

Excel diunduh sendiri dari idx.co.id (Data Pasar > Data Saham > Daftar Saham Marjin).
Pakai:  python buat_margin.py "Lamp ... .xlsx" --periode 2026-12 --sumber Peng-00xxx/BEI.POP/11-2026
Butuh:  openpyxl
Yang dibaca: sheet "1.b" (daftar efek yang dapat ditransaksikan secara margin).
Dua periode terakhir disimpan, supaya aplikasi tetap memakai daftar bulan berjalan sampai tanggal 1.
"""
import argparse
import json
import re
from pathlib import Path

import openpyxl

BERKAS = Path(__file__).with_name("margin.json")


def baca_kode(xlsx):
    ws = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)["1.b"]
    kode = set()
    for baris in ws.iter_rows(values_only=True):
        for sel in baris[:4]:
            if isinstance(sel, str) and re.fullmatch(r"[A-Z]{4}", sel.strip()):
                kode.add(sel.strip())
    return sorted(kode)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx")
    ap.add_argument("--periode", required=True, help="bulan berlaku, YYYY-MM")
    ap.add_argument("--sumber", required=True, help="nomor pengumuman BEI")
    ap.add_argument("--paksa", action="store_true", help="tetap tulis walau jumlahnya berubah > 25%%")
    a = ap.parse_args()
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", a.periode):
        raise SystemExit("--periode harus YYYY-MM")
    kode = baca_kode(a.xlsx)
    if len(kode) < 100:
        raise SystemExit(f"Hanya {len(kode)} kode terbaca; format Excel mungkin berubah. Tidak ditulis.")

    lama = json.loads(BERKAS.read_text())["daftar"] if BERKAS.exists() else []
    sisa = [d for d in lama if d["periode"] != a.periode]
    sebelum = max((d for d in sisa if d["periode"] < a.periode), key=lambda d: d["periode"], default=None)
    if sebelum:
        s, k = set(sebelum["kode"]), set(kode)
        print(f"Dibanding {sebelum['periode']}: masuk {len(k - s)}: {' '.join(sorted(k - s))}")
        print(f"                  keluar {len(s - k)}: {' '.join(sorted(s - k))}")
        if abs(len(k) - len(s)) > 0.25 * len(s) and not a.paksa:
            raise SystemExit(f"Jumlah berubah {len(s)} -> {len(k)}. Periksa dulu, lalu pakai --paksa.")

    daftar = sorted(sisa + [{"periode": a.periode, "sumber": a.sumber, "kode": kode}], key=lambda d: d["periode"])[-2:]
    BERKAS.write_text(json.dumps({"versi": 1, "daftar": daftar}, separators=(",", ":")) + "\n")
    print(f"margin.json ditulis: {a.periode} = {len(kode)} kode")


if __name__ == "__main__":
    main()
