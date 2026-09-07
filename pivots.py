"""
Detectare pivot points (extreme locale) din serii de preturi OHLC.
Aceasta e baza geometrica pentru toate pattern-urile: H&S, Double Top/Bottom,
triunghiuri, trendlines etc se construiesc pe pivot highs/lows.
"""
import numpy as np
import pandas as pd


def find_pivots(df, left=3, right=3):
    """
    Gaseste pivot highs si pivot lows folosind o fereastra simetrica.
    Un pivot high la indexul i inseamna ca high[i] e maximul strict din
    fereastra [i-left, i+right]. Similar pentru pivot low cu minime.

    df: DataFrame cu coloane High, Low, Close, Volume (index = date)
    left, right: cate bare in stanga/dreapta trebuie sa fie mai mici/mari

    Returns: (pivot_highs, pivot_lows) - fiecare e o lista de tuple
             (index_pozitie, data, pret)
    """
    highs = df['High'].values
    lows = df['Low'].values
    n = len(df)

    pivot_highs = []
    pivot_lows = []

    for i in range(left, n - right):
        window_h = highs[i - left:i + right + 1]
        if highs[i] == window_h.max() and np.argmax(window_h) == left:
            pivot_highs.append((i, df.index[i], highs[i]))

        window_l = lows[i - left:i + right + 1]
        if lows[i] == window_l.min() and np.argmin(window_l) == left:
            pivot_lows.append((i, df.index[i], lows[i]))

    return pivot_highs, pivot_lows


def merge_nearby_pivots(pivots, min_gap=3):
    """
    Daca doua pivoturi de acelasi tip sunt prea aproape (in bare), pastreaza-l
    pe cel mai extrem. Evita zgomot de la pivoturi minore adiacente.
    """
    if not pivots:
        return pivots
    merged = [pivots[0]]
    for p in pivots[1:]:
        last = merged[-1]
        if p[0] - last[0] < min_gap:
            merged[-1] = p
        else:
            merged.append(p)
    return merged


def avg_volume(df, window=20):
    """Media mobila a volumului pe ultimele `window` bare (exclusiv ultima bara)."""
    return df['Volume'].rolling(window).mean()


def volume_confirms(df, at_index, multiplier=1.5, window=20):
    """
    Verifica daca volumul la bara `at_index` e semnificativ peste medie
    (semnal de confirmare pentru un breakout).
    """
    if at_index < window:
        return False, None
    avg = df['Volume'].iloc[at_index - window:at_index].mean()
    vol = df['Volume'].iloc[at_index]
    ratio = vol / avg if avg > 0 else 0
    return ratio >= multiplier, ratio
