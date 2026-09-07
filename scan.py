"""
Chart Pattern Scout - scanner principal.
Descarca date Yahoo Finance pentru watchlist, detecteaza pattern-uri geometrice,
confirma cu volum, deseneaza chart-uri, genereaza raport HTML.

Ruleaza din GitHub Actions (are acces liber la Yahoo Finance).
Usage: python scan.py [--interval 1d|1wk] [--outdir docs]
"""
import argparse
import json
import os
import time
import traceback
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf

from tickers import TICKERS, get_sector, get_display_name, SECTOR_BENCHMARKS
from patterns import detect_all_patterns
from plotting import plot_pattern

MIN_QUALITY = 55  # praga minima ca un pattern sa apara in raport
STATE_FILE = 'scan_state.json'


def download(symbol, interval='1d', period='1y'):
    """Descarca date OHLCV pentru un simbol. Returneaza DataFrame sau None."""
    try:
        df = yf.download(symbol, period=period, interval=interval,
                          progress=False, auto_adjust=True, multi_level_index=False)
        if df is None or df.empty or len(df) < 30:
            return None
        df = df.dropna()
        return df
    except Exception as e:
        print(f'  [ERR] {symbol}: {e}')
        return None


def load_state(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def save_state(path, state):
    with open(path, 'w') as f:
        json.dump(state, f, indent=2, default=str)


def pattern_key(symbol, interval, pattern):
    """Cheie unica pt a compara acelasi pattern intre rulari succesive."""
    pts = pattern.get('points', {})
    anchor = ''
    for v in pts.values():
        if isinstance(v, tuple) and len(v) == 2:
            anchor = str(v[0])
            break
    return f"{symbol}|{interval}|{pattern['type']}|{anchor}"


def run_scan(interval='1d', outdir='docs', lookback_period='1y'):
    os.makedirs(outdir, exist_ok=True)
    charts_dir = os.path.join(outdir, 'charts')
    os.makedirs(charts_dir, exist_ok=True)

    state_path = os.path.join(outdir, STATE_FILE)
    prev_state = load_state(state_path)
    new_state = {}

    all_hits = []
    errors = []
    symbols = list(TICKERS.keys())

    print(f'Scanare {len(symbols)} tickere, interval={interval}...')
    for i, symbol in enumerate(symbols):
        print(f'[{i+1}/{len(symbols)}] {symbol}...')
        df = download(symbol, interval=interval, period=lookback_period)
        if df is None:
            errors.append(symbol)
            continue

        try:
            patterns = detect_all_patterns(df)
        except Exception as e:
            print(f'  [ERR detect] {symbol}: {e}')
            traceback.print_exc()
            errors.append(symbol)
            continue

        for p in patterns:
            if p['quality_score'] < MIN_QUALITY:
                continue
            key = pattern_key(symbol, interval, p)
            is_new = key not in prev_state
            new_state[key] = {
                'first_seen': prev_state.get(key, {}).get('first_seen', datetime.now(timezone.utc).isoformat()),
                'status': p['status'],
            }
            status_changed = prev_state.get(key, {}).get('status') != p['status']

            chart_path = None
            if is_new or status_changed or p['status'] == 'confirmed':
                safe_type = p['type'].replace(' ', '_').replace('&', 'and').replace('/', '-').replace('(', '').replace(')', '')
                fname = f"{symbol.replace('.', '_').replace('-', '_')}_{interval}_{safe_type}.png"
                fpath = os.path.join(charts_dir, fname)
                try:
                    plot_pattern(df, p, get_display_name(symbol), out_path=fpath)
                    chart_path = f"charts/{fname}"
                except Exception as e:
                    print(f'  [ERR plot] {symbol} {p["type"]}: {e}')

            all_hits.append({
                'symbol': symbol,
                'name': get_display_name(symbol),
                'sector': get_sector(symbol),
                'interval': interval,
                'pattern': p,
                'is_new': is_new,
                'status_changed': status_changed,
                'chart_path': chart_path,
                'last_price': round(float(df['Close'].iloc[-1]), 4),
            })

        time.sleep(0.3)  # fii politicos cu Yahoo

    save_state(state_path, new_state)

    print(f'\nGata. {len(all_hits)} hit-uri peste prag calitate, {len(errors)} erori de descarcare.')
    if errors:
        print('Simboluri esuate:', errors)

    return all_hits, errors


if __name__ == '__main__':
    from report import generate_report

    ap = argparse.ArgumentParser()
    ap.add_argument('--interval', default='1d', choices=['1d', '1wk'])
    ap.add_argument('--outdir', default='docs')
    args = ap.parse_args()
    hits, errors = run_scan(interval=args.interval, outdir=args.outdir)
    out_path = generate_report(hits, errors, outdir=args.outdir, interval=args.interval)
    print(f'Raport generat: {out_path}')
