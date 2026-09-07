"""
Detectori de pattern-uri geometrice clasice, bazati pe pivot points.
Fiecare detector returneaza o lista de dict-uri cu:
  type, status (forming/confirmed/invalidated), trigger_price,
  invalidation_price, quality_score (0-100), points (pentru desenare), notes
"""
import numpy as np
from pivots import find_pivots, volume_confirms


def _pct_diff(a, b):
    return abs(a - b) / ((a + b) / 2)


def detect_double_top(df, pivot_highs, pivot_lows, tol=0.03):
    """Doua varfuri apropiate ca pret, separate de un pullback (neckline)."""
    results = []
    for i in range(len(pivot_highs) - 1):
        idx1, date1, price1 = pivot_highs[i]
        idx2, date2, price2 = pivot_highs[i + 1]
        if idx2 - idx1 < 5:
            continue
        if _pct_diff(price1, price2) > tol:
            continue
        # neckline = minimul dintre cele doua varfuri
        between_lows = [p for p in pivot_lows if idx1 < p[0] < idx2]
        if not between_lows:
            continue
        neckline = min(between_lows, key=lambda p: p[2])
        neckline_price = neckline[2]

        current_price = df['Close'].iloc[-1]
        last_idx = len(df) - 1
        broke_down = current_price < neckline_price and last_idx > idx2

        quality = 100 - min(_pct_diff(price1, price2) * 1000, 40)
        depth = _pct_diff((price1 + price2) / 2, neckline_price)
        if depth < 0.03:
            quality -= 20

        status = 'confirmed' if broke_down else 'forming'
        vol_ok, vol_ratio = volume_confirms(df, last_idx) if broke_down else (None, None)

        results.append({
            'type': 'Double Top',
            'status': status,
            'trigger_price': round(neckline_price, 2),
            'invalidation_price': round(max(price1, price2) * 1.02, 2),
            'quality_score': round(max(quality, 0)),
            'points': {'peak1': (date1, price1), 'peak2': (date2, price2),
                       'neckline': (neckline[1], neckline_price)},
            'volume_confirmed': vol_ok,
            'volume_ratio': round(vol_ratio, 2) if vol_ratio else None,
            'notes': f'Neckline la {neckline_price:.2f}' + (' - SPART' if broke_down else ' - in asteptare')
        })
    return results


def detect_double_bottom(df, pivot_highs, pivot_lows, tol=0.03):
    """Doua funduri apropiate ca pret, separate de un revenire (neckline)."""
    results = []
    for i in range(len(pivot_lows) - 1):
        idx1, date1, price1 = pivot_lows[i]
        idx2, date2, price2 = pivot_lows[i + 1]
        if idx2 - idx1 < 5:
            continue
        if _pct_diff(price1, price2) > tol:
            continue
        between_highs = [p for p in pivot_highs if idx1 < p[0] < idx2]
        if not between_highs:
            continue
        neckline = max(between_highs, key=lambda p: p[2])
        neckline_price = neckline[2]

        current_price = df['Close'].iloc[-1]
        last_idx = len(df) - 1
        broke_up = current_price > neckline_price and last_idx > idx2

        quality = 100 - min(_pct_diff(price1, price2) * 1000, 40)
        depth = _pct_diff((price1 + price2) / 2, neckline_price)
        if depth < 0.03:
            quality -= 20

        status = 'confirmed' if broke_up else 'forming'
        vol_ok, vol_ratio = volume_confirms(df, last_idx) if broke_up else (None, None)

        results.append({
            'type': 'Double Bottom',
            'status': status,
            'trigger_price': round(neckline_price, 2),
            'invalidation_price': round(min(price1, price2) * 0.98, 2),
            'quality_score': round(max(quality, 0)),
            'points': {'trough1': (date1, price1), 'trough2': (date2, price2),
                       'neckline': (neckline[1], neckline_price)},
            'volume_confirmed': vol_ok,
            'volume_ratio': round(vol_ratio, 2) if vol_ratio else None,
            'notes': f'Neckline la {neckline_price:.2f}' + (' - SPART' if broke_up else ' - in asteptare')
        })
    return results


def detect_head_shoulders(df, pivot_highs, pivot_lows, tol=0.05):
    """Umar-Cap-Umar: 3 varfuri, cel din mijloc mai inalt, umerii aprox egali."""
    results = []
    for i in range(len(pivot_highs) - 2):
        idx1, date1, p1 = pivot_highs[i]
        idx2, date2, p2 = pivot_highs[i + 1]
        idx3, date3, p3 = pivot_highs[i + 2]
        if not (p2 > p1 and p2 > p3):
            continue
        if _pct_diff(p1, p3) > tol:
            continue
        between1 = [p for p in pivot_lows if idx1 < p[0] < idx2]
        between2 = [p for p in pivot_lows if idx2 < p[0] < idx3]
        if not between1 or not between2:
            continue
        low1 = min(between1, key=lambda p: p[2])
        low2 = min(between2, key=lambda p: p[2])
        neckline_price = (low1[2] + low2[2]) / 2

        current_price = df['Close'].iloc[-1]
        last_idx = len(df) - 1
        broke_down = current_price < neckline_price and last_idx > idx3

        quality = 100 - min(_pct_diff(p1, p3) * 800, 30) - min(_pct_diff(low1[2], low2[2]) * 500, 20)
        status = 'confirmed' if broke_down else 'forming'
        vol_ok, vol_ratio = volume_confirms(df, last_idx) if broke_down else (None, None)

        results.append({
            'type': 'Head & Shoulders',
            'status': status,
            'trigger_price': round(neckline_price, 2),
            'invalidation_price': round(p2 * 1.02, 2),
            'quality_score': round(max(quality, 0)),
            'points': {'left_shoulder': (date1, p1), 'head': (date2, p2),
                       'right_shoulder': (date3, p3),
                       'neckline_l': (low1[1], low1[2]), 'neckline_r': (low2[1], low2[2])},
            'volume_confirmed': vol_ok,
            'volume_ratio': round(vol_ratio, 2) if vol_ratio else None,
            'notes': f'Neckline ~{neckline_price:.2f}' + (' - SPART' if broke_down else ' - in asteptare')
        })
    return results


def detect_inverse_head_shoulders(df, pivot_highs, pivot_lows, tol=0.05):
    """Inversul H&S: 3 funduri, cel din mijloc mai jos, umerii aprox egali."""
    results = []
    for i in range(len(pivot_lows) - 2):
        idx1, date1, p1 = pivot_lows[i]
        idx2, date2, p2 = pivot_lows[i + 1]
        idx3, date3, p3 = pivot_lows[i + 2]
        if not (p2 < p1 and p2 < p3):
            continue
        if _pct_diff(p1, p3) > tol:
            continue
        between1 = [p for p in pivot_highs if idx1 < p[0] < idx2]
        between2 = [p for p in pivot_highs if idx2 < p[0] < idx3]
        if not between1 or not between2:
            continue
        high1 = max(between1, key=lambda p: p[2])
        high2 = max(between2, key=lambda p: p[2])
        neckline_price = (high1[2] + high2[2]) / 2

        current_price = df['Close'].iloc[-1]
        last_idx = len(df) - 1
        broke_up = current_price > neckline_price and last_idx > idx3

        quality = 100 - min(_pct_diff(p1, p3) * 800, 30) - min(_pct_diff(high1[2], high2[2]) * 500, 20)
        status = 'confirmed' if broke_up else 'forming'
        vol_ok, vol_ratio = volume_confirms(df, last_idx) if broke_up else (None, None)

        results.append({
            'type': 'Inverse Head & Shoulders',
            'status': status,
            'trigger_price': round(neckline_price, 2),
            'invalidation_price': round(p2 * 0.98, 2),
            'quality_score': round(max(quality, 0)),
            'points': {'left_shoulder': (date1, p1), 'head': (date2, p2),
                       'right_shoulder': (date3, p3),
                       'neckline_l': (high1[1], high1[2]), 'neckline_r': (high2[1], high2[2])},
            'volume_confirmed': vol_ok,
            'volume_ratio': round(vol_ratio, 2) if vol_ratio else None,
            'notes': f'Neckline ~{neckline_price:.2f}' + (' - SPART' if broke_up else ' - in asteptare')
        })
    return results


def detect_triangle(df, pivot_highs, pivot_lows, lookback=60, min_points=2):
    """
    Triunghi ascendent/descendent/simetric: regresie liniara pe pivot highs
    si pivot lows recente, verifica convergenta pantelor.
    """
    results = []
    n = len(df)
    start_idx = max(0, n - lookback)

    recent_highs = [p for p in pivot_highs if p[0] >= start_idx]
    recent_lows = [p for p in pivot_lows if p[0] >= start_idx]

    if len(recent_highs) < min_points or len(recent_lows) < min_points:
        return results

    hx = np.array([p[0] for p in recent_highs])
    hy = np.array([p[2] for p in recent_highs])
    lx = np.array([p[0] for p in recent_lows])
    ly = np.array([p[2] for p in recent_lows])

    slope_h, intercept_h = np.polyfit(hx, hy, 1)
    slope_l, intercept_l = np.polyfit(lx, ly, 1)

    avg_price = df['Close'].iloc[start_idx:].mean()
    slope_h_norm = slope_h / avg_price
    slope_l_norm = slope_l / avg_price

    flat_thresh = 0.0005

    ttype = None
    if abs(slope_h_norm) < flat_thresh and slope_l_norm > flat_thresh:
        ttype = 'Triunghi ascendent'
    elif slope_h_norm < -flat_thresh and abs(slope_l_norm) < flat_thresh:
        ttype = 'Triunghi descendent'
    elif slope_h_norm < -flat_thresh and slope_l_norm > flat_thresh:
        ttype = 'Triunghi simetric'
    else:
        return results

    last_idx = n - 1
    upper_now = slope_h * last_idx + intercept_h
    lower_now = slope_l * last_idx + intercept_l
    current_price = df['Close'].iloc[-1]

    width_start = (slope_h * start_idx + intercept_h) - (slope_l * start_idx + intercept_l)
    width_now = upper_now - lower_now
    if width_start <= 0 or width_now / width_start > 0.9:
        return results

    broke_up = current_price > upper_now
    broke_down = current_price < lower_now
    status = 'confirmed' if (broke_up or broke_down) else 'forming'
    vol_ok, vol_ratio = volume_confirms(df, last_idx) if (broke_up or broke_down) else (None, None)

    quality = 70
    quality += min(len(recent_highs) + len(recent_lows), 8) * 3
    if width_now / width_start < 0.4:
        quality += 10

    direction = 'sus' if broke_up else ('jos' if broke_down else None)

    results.append({
        'type': ttype,
        'status': status,
        'trigger_price': round(upper_now if not broke_down else lower_now, 2),
        'invalidation_price': round(lower_now if not broke_down else upper_now, 2),
        'quality_score': round(min(quality, 100)),
        'points': {
            'upper_line': (slope_h, intercept_h, recent_highs[0][0], last_idx),
            'lower_line': (slope_l, intercept_l, recent_lows[0][0], last_idx),
            'highs': [(p[1], p[2]) for p in recent_highs],
            'lows': [(p[1], p[2]) for p in recent_lows],
        },
        'volume_confirmed': vol_ok,
        'volume_ratio': round(vol_ratio, 2) if vol_ratio else None,
        'notes': f'Breakout {direction}' if direction else 'Convergenta in desfasurare'
    })
    return results


def detect_rectangle(df, pivot_highs, pivot_lows, lookback=50, tol=0.025, min_touches=2):
    """Range orizontal: minim 2 atingeri sus si 2 jos, in aceeasi banda de pret."""
    results = []
    n = len(df)
    start_idx = max(0, n - lookback)

    recent_highs = [p for p in pivot_highs if p[0] >= start_idx]
    recent_lows = [p for p in pivot_lows if p[0] >= start_idx]
    if len(recent_highs) < min_touches or len(recent_lows) < min_touches:
        return results

    high_prices = [p[2] for p in recent_highs]
    low_prices = [p[2] for p in recent_lows]
    resistance = np.median(high_prices)
    support = np.median(low_prices)

    if _pct_diff(max(high_prices), min(high_prices)) > tol * 2:
        return results
    if _pct_diff(max(low_prices), min(low_prices)) > tol * 2:
        return results
    if resistance <= support:
        return results

    current_price = df['Close'].iloc[-1]
    last_idx = n - 1
    broke_up = current_price > resistance * (1 + tol / 2)
    broke_down = current_price < support * (1 - tol / 2)
    status = 'confirmed' if (broke_up or broke_down) else 'forming'
    vol_ok, vol_ratio = volume_confirms(df, last_idx) if (broke_up or broke_down) else (None, None)

    quality = 60 + min(len(recent_highs) + len(recent_lows), 10) * 4
    direction = 'sus' if broke_up else ('jos' if broke_down else None)

    results.append({
        'type': 'Rectangle / Range',
        'status': status,
        'trigger_price': round(resistance, 2),
        'invalidation_price': round(support, 2),
        'quality_score': round(min(quality, 100)),
        'points': {'resistance': resistance, 'support': support,
                   'highs': [(p[1], p[2]) for p in recent_highs],
                   'lows': [(p[1], p[2]) for p in recent_lows],
                   'start_date': df.index[start_idx]},
        'volume_confirmed': vol_ok,
        'volume_ratio': round(vol_ratio, 2) if vol_ratio else None,
        'notes': f'Range {support:.2f}-{resistance:.2f}' + (f', breakout {direction}' if direction else '')
    })
    return results


def detect_round_bottom(df, lookback=40, min_r2=0.5):
    """
    Round bottom / rounding top: fit polinomial grad 2 pe close, verifica
    curbura (semnul coeficientului) si calitatea fit-ului (R^2).
    """
    results = []
    n = len(df)
    start_idx = max(0, n - lookback)
    window = df.iloc[start_idx:]
    if len(window) < 15:
        return results

    x = np.arange(len(window))
    y = window['Close'].values
    coeffs = np.polyfit(x, y, 2)
    a, b, c = coeffs
    fitted = np.polyval(coeffs, x)

    ss_res = np.sum((y - fitted) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    if r2 < min_r2:
        return results

    vertex_x = -b / (2 * a) if a != 0 else None
    if vertex_x is None or not (0.15 * len(window) < vertex_x < 0.85 * len(window)):
        return results

    current_price = df['Close'].iloc[-1]
    last_idx = n - 1
    recent_high = window['Close'].iloc[int(vertex_x):].max() if int(vertex_x) < len(window) else current_price

    if a > 0:
        ptype = 'Round Bottom'
        broke_up = current_price > recent_high * 0.995 and current_price >= window['Close'].iloc[-5:].max()
        status = 'confirmed' if broke_up else 'forming'
        vol_ok, vol_ratio = volume_confirms(df, last_idx) if broke_up else (None, None)
        trigger = round(recent_high, 2)
        invalidation = round(y[int(vertex_x)] * 0.97, 2)
    else:
        ptype = 'Rounding Top'
        recent_low = window['Close'].iloc[int(vertex_x):].min() if int(vertex_x) < len(window) else current_price
        broke_down = current_price < recent_low * 1.005 and current_price <= window['Close'].iloc[-5:].min()
        status = 'confirmed' if broke_down else 'forming'
        vol_ok, vol_ratio = volume_confirms(df, last_idx) if broke_down else (None, None)
        trigger = round(recent_low, 2)
        invalidation = round(y[int(vertex_x)] * 1.03, 2)

    quality = round(r2 * 100)

    results.append({
        'type': ptype,
        'status': status,
        'trigger_price': trigger,
        'invalidation_price': invalidation,
        'quality_score': quality,
        'points': {'coeffs': coeffs.tolist(), 'start_idx': start_idx,
                   'dates': window.index.tolist(), 'fitted': fitted.tolist()},
        'volume_confirmed': vol_ok,
        'volume_ratio': round(vol_ratio, 2) if vol_ratio else None,
        'notes': f'R^2={r2:.2f}, curbura {"pozitiva (bottom)" if a > 0 else "negativa (top)"}'
    })
    return results


def detect_cup_handle(df, lookback=60, min_r2=0.45):
    """Cup & Handle: round bottom urmat de un mic pullback (handle) la final."""
    results = []
    n = len(df)
    start_idx = max(0, n - lookback)
    window = df.iloc[start_idx:]
    if len(window) < 25:
        return results

    cup_end = int(len(window) * 0.75)
    cup = window.iloc[:cup_end]
    handle = window.iloc[cup_end:]
    if len(cup) < 15 or len(handle) < 4:
        return results

    x = np.arange(len(cup))
    y = cup['Close'].values
    coeffs = np.polyfit(x, y, 2)
    a, b, c = coeffs
    fitted = np.polyval(coeffs, x)
    ss_res = np.sum((y - fitted) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    if r2 < min_r2 or a <= 0:
        return results

    cup_lip = max(cup['Close'].iloc[0], cup['Close'].iloc[-1])
    handle_low = handle['Close'].min()
    handle_depth = _pct_diff(cup_lip, handle_low)
    if handle_depth > 0.15:
        return results

    current_price = df['Close'].iloc[-1]
    last_idx = n - 1
    broke_up = current_price > cup_lip
    status = 'confirmed' if broke_up else 'forming'
    vol_ok, vol_ratio = volume_confirms(df, last_idx) if broke_up else (None, None)

    quality = round(r2 * 80 + (15 if handle_depth < 0.08 else 5))

    results.append({
        'type': 'Cup & Handle',
        'status': status,
        'trigger_price': round(cup_lip, 2),
        'invalidation_price': round(handle_low * 0.97, 2),
        'quality_score': min(quality, 100),
        'points': {'cup_coeffs': coeffs.tolist(), 'cup_start': start_idx,
                   'cup_end_idx': start_idx + cup_end, 'lip': cup_lip,
                   'handle_low': handle_low},
        'volume_confirmed': vol_ok,
        'volume_ratio': round(vol_ratio, 2) if vol_ratio else None,
        'notes': f'Lip la {cup_lip:.2f}' + (' - SPART' if broke_up else ' - in asteptare')
    })
    return results


def detect_trendlines(df, pivot_highs, pivot_lows, lookback=80, min_touches=2, tol=0.025):
    """
    Linii de trend (suport/rezistenta): grupeaza pivoturi ce ating aceeasi
    linie (regresie), raporteaza atingeri, apropiere curenta, breakout.
    """
    results = []
    n = len(df)
    start_idx = max(0, n - lookback)

    for label, pivots, is_support in [('rezistenta', pivot_highs, False), ('suport', pivot_lows, True)]:
        recent = [p for p in pivots if p[0] >= start_idx]
        if len(recent) < min_touches:
            continue

        best = None
        for i in range(len(recent) - 1):
            for j in range(i + 1, len(recent)):
                x1, _, y1 = recent[i]
                x2, _, y2 = recent[j]
                if x2 == x1:
                    continue
                slope = (y2 - y1) / (x2 - x1)
                intercept = y1 - slope * x1

                touches = []
                for p in recent:
                    line_y = slope * p[0] + intercept
                    if _pct_diff(p[2], line_y) < tol:
                        touches.append(p)
                if len(touches) >= min_touches:
                    if best is None or len(touches) > len(best['touches']):
                        best = {'slope': slope, 'intercept': intercept, 'touches': touches}

        if best is None:
            continue

        last_idx = n - 1
        line_now = best['slope'] * last_idx + best['intercept']
        current_price = df['Close'].iloc[-1]
        proximity = _pct_diff(current_price, line_now)

        if is_support:
            broke = current_price < line_now * (1 - tol)
        else:
            broke = current_price > line_now * (1 + tol)

        near = proximity < tol * 1.5

        if not (broke or near):
            continue

        status = 'confirmed' if broke else 'forming'
        vol_ok, vol_ratio = volume_confirms(df, last_idx) if broke else (None, None)
        quality = 50 + len(best['touches']) * 10

        results.append({
            'type': f'Linie de trend ({label})',
            'status': status,
            'trigger_price': round(line_now, 2),
            'invalidation_price': None,
            'quality_score': min(quality, 100),
            'points': {'slope': best['slope'], 'intercept': best['intercept'],
                       'touches': [(p[1], p[2]) for p in best['touches']],
                       'start_idx': start_idx, 'end_idx': last_idx},
            'volume_confirmed': vol_ok,
            'volume_ratio': round(vol_ratio, 2) if vol_ratio else None,
            'notes': f'{len(best["touches"])} atingeri' + (', SPARTA' if broke else ', pret apropiat')
        })
    return results


def _dedupe(results, tol=0.015):
    """Elimina hit-uri duplicate de acelasi tip cu trigger_price aproape identic."""
    seen = []
    out = []
    for r in results:
        tp = r.get('trigger_price')
        dup = False
        for r2 in seen:
            if r2['type'] == r['type'] and tp is not None and r2.get('trigger_price') is not None:
                if _pct_diff(tp, r2['trigger_price']) < tol:
                    dup = True
                    break
        if not dup:
            seen.append(r)
            out.append(r)
    return out


def detect_all_patterns(df):
    """Ruleaza toti detectorii pe un DataFrame OHLCV si aduna rezultatele."""
    pivot_highs, pivot_lows = find_pivots(df, left=3, right=3)

    all_results = []
    all_results += detect_double_top(df, pivot_highs, pivot_lows)
    all_results += detect_double_bottom(df, pivot_highs, pivot_lows)
    all_results += detect_head_shoulders(df, pivot_highs, pivot_lows)
    all_results += detect_inverse_head_shoulders(df, pivot_highs, pivot_lows)
    all_results += detect_triangle(df, pivot_highs, pivot_lows)
    all_results += detect_rectangle(df, pivot_highs, pivot_lows)
    all_results += detect_round_bottom(df)
    all_results += detect_cup_handle(df)
    all_results += detect_trendlines(df, pivot_highs, pivot_lows)

    return _dedupe(all_results)
