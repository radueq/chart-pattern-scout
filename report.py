"""Genereaza raportul HTML din hit-urile scanarii."""
import os
from datetime import datetime, timezone

STATUS_LABELS = {
    'confirmed': ('Confirmat', '#0F6E56'),
    'forming': ('In formare', '#854F0B'),
}


def _pattern_card(hit):
    p = hit['pattern']
    status_label, status_color = STATUS_LABELS.get(p['status'], (p['status'], '#5F5E5A'))
    badges = []
    if hit['is_new']:
        badges.append('<span class="badge new">nou</span>')
    elif hit['status_changed']:
        badges.append('<span class="badge changed">schimbat</span>')
    vol_note = ''
    if p.get('volume_confirmed') is True:
        vol_note = f'<span class="badge vol-ok">volum confirmat ({p.get("volume_ratio")}x medie)</span>'
    elif p.get('volume_confirmed') is False:
        vol_note = f'<span class="badge vol-weak">volum slab ({p.get("volume_ratio")}x medie)</span>'

    img_html = ''
    if hit['chart_path']:
        img_html = f'<img src="{hit["chart_path"]}" alt="{hit["symbol"]} {p["type"]}" loading="lazy">'

    invalid_line = f'<div class="metric"><span>Invalidare</span><strong>{p["invalidation_price"]}</strong></div>' if p.get('invalidation_price') else ''

    return f'''
    <div class="card">
      <div class="card-head">
        <div>
          <span class="ticker">{hit['symbol']}</span>
          <span class="name">{hit['name']}</span>
        </div>
        <div class="badges">{''.join(badges)}</div>
      </div>
      <div class="pattern-title">{p['type']} <span class="interval">({hit['interval']})</span></div>
      <div class="status" style="color:{status_color}">{status_label}</div>
      {img_html}
      <div class="metrics">
        <div class="metric"><span>Pret curent</span><strong>{hit['last_price']}</strong></div>
        <div class="metric"><span>Trigger</span><strong>{p['trigger_price']}</strong></div>
        {invalid_line}
        <div class="metric"><span>Calitate</span><strong>{p['quality_score']}/100</strong></div>
      </div>
      <div class="notes">{p['notes']} {vol_note}</div>
    </div>
    '''


def generate_report(all_hits, errors, outdir='docs', interval='1d'):
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    new_or_changed = [h for h in all_hits if h['is_new'] or h['status_changed']]
    confirmed = [h for h in all_hits if h['pattern']['status'] == 'confirmed']
    forming = [h for h in all_hits if h['pattern']['status'] == 'forming']

    new_or_changed.sort(key=lambda h: -h['pattern']['quality_score'])
    confirmed.sort(key=lambda h: -h['pattern']['quality_score'])
    forming.sort(key=lambda h: -h['pattern']['quality_score'])

    def section(title, hits):
        if not hits:
            return f'<h2>{title}</h2><p class="empty">Niciun hit.</p>'
        cards = ''.join(_pattern_card(h) for h in hits)
        return f'<h2>{title} ({len(hits)})</h2><div class="grid">{cards}</div>'

    html = f'''<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chart Pattern Scout</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; background: #F1EFE8; color: #2C2C2A; margin: 0; padding: 1rem; }}
  h1 {{ font-size: 20px; margin: 0 0 4px; }}
  .meta {{ font-size: 13px; color: #5F5E5A; margin-bottom: 1.5rem; }}
  h2 {{ font-size: 16px; margin: 1.5rem 0 0.75rem; border-top: 1px solid #D3D1C7; padding-top: 1rem; }}
  .empty {{ font-size: 13px; color: #888780; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 12px; }}
  .card {{ background: white; border: 1px solid #D3D1C7; border-radius: 12px; padding: 12px; }}
  .card-head {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px; }}
  .ticker {{ font-weight: 600; font-size: 15px; margin-right: 6px; }}
  .name {{ font-size: 12px; color: #5F5E5A; }}
  .pattern-title {{ font-size: 14px; font-weight: 500; margin-top: 4px; }}
  .interval {{ font-size: 11px; color: #888780; font-weight: 400; }}
  .status {{ font-size: 12px; font-weight: 600; margin-bottom: 6px; }}
  img {{ width: 100%; border-radius: 8px; margin: 6px 0; display: block; }}
  .metrics {{ display: flex; flex-wrap: wrap; gap: 10px; font-size: 12px; margin: 6px 0; }}
  .metric {{ display: flex; flex-direction: column; }}
  .metric span {{ color: #888780; font-size: 10px; }}
  .metric strong {{ font-size: 13px; }}
  .notes {{ font-size: 11px; color: #5F5E5A; margin-top: 4px; }}
  .badge {{ font-size: 10px; padding: 2px 8px; border-radius: 10px; margin-left: 4px; }}
  .badge.new {{ background: #C0DD97; color: #173404; }}
  .badge.changed {{ background: #FAC775; color: #412402; }}
  .badge.vol-ok {{ background: #9FE1CB; color: #04342C; }}
  .badge.vol-weak {{ background: #F0997B; color: #4A1B0C; }}
</style>
</head>
<body>
  <h1>Chart Pattern Scout</h1>
  <div class="meta">Ultima scanare: {now} · interval {interva
