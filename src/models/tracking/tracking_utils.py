# models/tracking_utils.py
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def price_bucket_of(p):
    if p is None: return 'sin_precio'
    try:
        p = float(p)
    except:
        return 'sin_precio'
    if p < 10: return '<10'
    if p < 20: return '10-19'
    if p < 50: return '20-49'
    if p < 100: return '50-99'
    return '100+'

def discount_pct_of(precio, precio_original):
    try:
        if precio and precio_original and float(precio_original) > 0:
            return round(100.0 * (1.0 - float(precio)/float(precio_original)), 2)
    except:
        pass
    return None

def append_params(url, extra_params: dict) -> str:
    parts = list(urlparse(url))
    q = parse_qs(parts[4], keep_blank_values=True)
    for k, v in extra_params.items():
        if v is None: 
            continue
        q[k] = [str(v)]
    parts[4] = urlencode(q, doseq=True)
    return urlunparse(parts)
