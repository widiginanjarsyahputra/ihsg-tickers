"""Validasi kontrak feed screener publik sebelum publikasi. Hasil AI pribadi tidak ikut feed."""
import argparse
import json
import math
from pathlib import Path


def validasi(d):
    if d.get('versi') != 2:
        raise ValueError('Feed baru harus versi 2')
    if d.get('top') != []:
        raise ValueError('Prioritas ditentukan oleh hasil AI perangkat, bukan server')
    if not d.get('status_valid') and any(p.get('aktif') for p in d['preset']):
        raise ValueError('Status basi tidak boleh diaktifkan')
    ids=set()
    for p in d['preset']:
        if p['id'] in ids: raise ValueError('Preset duplikat')
        ids.add(p['id'])
        if p['jenis'] not in ('induk','varian','eksperimen') or p['riset'] == p['aktif']:
            raise ValueError('Jenis dan status preset tidak valid')
        if not p['aktif'] and p['kandidat']:
            raise ValueError('Nonaktif tidak boleh masuk screener harian')
        for k in p['kandidat']:
            if k['label'] not in ('SIAP','PANTAU') or k['prioritas']:
                raise ValueError('Kandidat harian tidak valid')
            if not all(math.isfinite(k[n]) for n in ('sl','close','tp')) or not 0<k['sl']<k['close']<k['tp']:
                raise ValueError('Rencana harga tidak valid')
            if k['siap_ai'] and (k['label']!='SIAP' or k['skor']<70 or d.get('alasan')):
                raise ValueError('Kandidat AI tidak memenuhi pagar')
    return True


if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('file',type=Path);a=ap.parse_args()
    validasi(json.loads(a.file.read_text()));print('Feed screener versi 2 valid')
