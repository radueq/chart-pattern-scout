"""
Deseneaza chart-uri candlestick + volum, cu geometria pattern-ului suprapusa.
Foloseste mplfinance pentru candele, matplotlib pentru overlay-uri custom.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf


PATTERN_COLOR = '#D85A30'
TRIGGER_COLOR = '#1D9E75'
INVALID_COLOR = '#E24B4A'


def _base_plot(df, title, lookback=None):
    """Creeaza figura candlestick + volum, returneaza (fig, ax_price, ax_vol)."""
    plot_df = df.iloc[-lookback:] if lookback else df
    mc = mpf.make_marketcolors(up='#1D9E75', down='#E24B4A', edge='inherit', wick='inherit', volume='inherit')
    style = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', gridcolor='#888780', gridaxis='both', facecolor='white', figcolor='white')
    fig, axes = mpf.plot(plot_df, type='candle', style=style, volume=True,
                          returnfig=True, figsize=(9, 6), title=title,
                          tight_layout=False, datetime_format='%d-%b', xrotation=30)
    ax_price = axes[0]
    ax_vol = axes[2] if len(axes) > 2 else axes[1]
    return fig, ax_price, ax_vol, plot_df


def _date_to_xnum(plot_df, date):
    """Converteste o data in coordonata x folosita de mplfinance (index pozitional)."""
    if date in plot_df.index:
        return plot_df.index.get_loc(date)
    idx = plot_df.index.get_indexer([date], method='nearest')[0]
    return idx


def plot_pattern(df, pattern, ticker, lookback=90, out_path='pattern.png'):
    """
    Deseneaza chart-ul pentru un pattern detectat, cu geometria suprapusa.
    pattern: dict din detect_all_patterns()
    """
    ptype = pattern['type']
    title = f"{ticker} — {ptype} ({pattern['status']})"
    fig, ax, ax_vol, plot_df = _base_plot(df, title, lookback=lookback)

    pts = pattern.get('points', {})

    try:
        if ptype in ('Double Top', 'Double Bottom'):
            _draw_double(ax, plot_df, pts, ptype)
        elif ptype in ('Head & Shoulders', 'Inverse Head & Shoulders'):
            _draw_hs(ax, plot_df, pts, ptype)
        elif 'Triunghi' in ptype:
            _draw_triangle(ax, plot_df, pts)
        elif ptype == 'Rectangle / Range':
            _draw_rectangle(ax, plot_df, pts)
        elif ptype in ('Round Bottom', 'Rounding Top'):
            _draw_round(ax, plot_df, pts)
        elif ptype == 'Cup & Handle':
            _draw_cup(ax, plot_df, pts)
        elif 'trend' in ptype.lower():
            _draw_trendline(ax, plot_df, pts)
    except Exception as e:
        ax.text(0.02, 0.02, f'(overlay skip: {e})', transform=ax.transAxes, fontsize=7, color='gray')

    trigger = pattern.get('trigger_price')
    if trigger:
        ax.axhline(trigger, color=TRIGGER_COLOR, linestyle='--', linewidth=1, alpha=0.8)
        ax.text(len(plot_df) - 1, trigger, f' trigger {trigger}', color=TRIGGER_COLOR, fontsize=8, va='bottom')

    invalid = pattern.get('invalidation_price')
    if invalid:
        ax.axhline(invalid, color=INVALID_COLOR, linestyle=':', linewidth=1, alpha=0.7)
        ax.text(len(plot_df) - 1, invalid, f' invalid {invalid}', color=INVALID_COLOR, fontsize=8, va='top')

    fig.savefig(out_path, dpi=110, bbox_inches='tight')
    plt.close(fig)
    return out_path


def _xloc(plot_df, date):
    try:
        return plot_df.index.get_loc(date)
    except KeyError:
        return plot_df.index.get_indexer([date], method='nearest')[0]


def _draw_double(ax, plot_df, pts, ptype):
    if ptype == 'Double Top':
        p1, p2, neck = pts['peak1'], pts['peak2'], pts['neckline']
    else:
        p1, p2, neck = pts['trough1'], pts['trough2'], pts['neckline']
    x1, x2 = _xloc(plot_df, p1[0]), _xloc(plot_df, p2[0])
    xn = _xloc(plot_df, neck[0])
    ax.plot([x1, x2], [p1[1], p2[1]], color=PATTERN_COLOR, linewidth=1.5, marker='o', markersize=4)
    ax.plot([x1, xn, x2], [p1[1], neck[1], p2[1]], color=PATTERN_COLOR, linewidth=1, linestyle='--', alpha=0.6)


def _draw_hs(ax, plot_df, pts, ptype):
    ls, head, rs = pts['left_shoulder'], pts['head'], pts['right_shoulder']
    nl, nr = pts['neckline_l'], pts['neckline_r']
    xs = [_xloc(plot_df, p[0]) for p in [ls, head, rs]]
    ys = [p[1] for p in [ls, head, rs]]
    ax.plot(xs, ys, color=PATTERN_COLOR, linewidth=1.5, marker='o', markersize=4)
    xnl, xnr = _xloc(plot_df, nl[0]), _xloc(plot_df, nr[0])
    ax.plot([xnl, xnr], [nl[1], nr[1]], color=PATTERN_COLOR, linewidth=1.2, linestyle='--')


def _draw_triangle(ax, plot_df, pts):
    slope_h, intercept_h, x0, x1 = pts['upper_line']
    slope_l, intercept_l, lx0, lx1 = pts['lower_line']
    xs = np.array([min(x0, lx0), max(x1, lx1)])
    ax.plot(xs, slope_h * xs + intercept_h, color=PATTERN_COLOR, linewidth=1.3)
    ax.plot(xs, slope_l * xs + intercept_l, color=PATTERN_COLOR, linewidth=1.3)
    for date, price in pts.get('highs', []) + pts.get('lows', []):
        ax.plot(_xloc(plot_df, date), price, 'o', color=PATTERN_COLOR, markersize=4)


def _draw_rectangle(ax, plot_df, pts):
    start_x = _xloc(plot_df, pts['start_date'])
    end_x = len(plot_df) - 1
    ax.plot([start_x, end_x], [pts['resistance']] * 2, color=PATTERN_COLOR, linewidth=1.3)
    ax.plot([start_x, end_x], [pts['support']] * 2, color=PATTERN_COLOR, linewidth=1.3)
    ax.fill_between([start_x, end_x], pts['support'], pts['resistance'], color=PATTERN_COLOR, alpha=0.06)


def _draw_round(ax, plot_df, pts):
    dates = pts['dates']
    fitted = pts['fitted']
    xs = [_xloc(plot_df, d) for d in dates]
    ax.plot(xs, fitted, color=PATTERN_COLOR, linewidth=1.8)


def _draw_cup(ax, plot_df, pts):
    lip = pts['lip']
    ax.axhline(lip, color=PATTERN_COLOR, linewidth=1.3, linestyle='-', alpha=0.7)
    ax.axhline(pts['handle_low'], color=PATTERN_COLOR, linewidth=1, linestyle=':', alpha=0.6)


def _draw_trendline(ax, plot_df, pts):
    slope, intercept = pts['slope'], pts['intercept']
    x0, x1 = pts['start_idx'], pts['end_idx']
    xs = np.array([x0, x1])
    n = len(plot_df)
    xs = np.clip(xs, 0, n - 1)
    ax.plot(xs, slope * xs + intercept, color=PATTERN_COLOR, linewidth=1.5)
    for date, price in pts.get('touches', []):
        ax.plot(_xloc(plot_df, date), price, 'o', color=PATTERN_COLOR, markersize=4)
