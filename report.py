"""Genereaza raportul HTML din hit-urile scanarii."""
import os
from datetime import datetime, timezone

STATUS_LABELS = {
    'confirmed': ('Confirmat', '#0F6E56'),
    'forming': ('In formare', '#854F0B'),
}

CSS = (
    "body { font-family: -apple-system, Segoe UI, Roboto, sans-serif; "
    "background: #F1EFE8; color: #2C2C2A; margin: 0; padding: 1rem; }\n"
    "h1 { font-size: 20px; margin: 0 0 4px; }\n"
    ".meta { font-size: 13px; color: #5F5E5A; margin-bottom: 1.5rem; }\n"
    "h2 { font-size: 16px; margin: 1.5rem 0 0.75rem; border-top: 1px solid #D3D1C7; padding-top: 1rem; }\n"
    ".empty { font-size: 13px; color: #888780; }\n"
    ".grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 12px; }\n"
    ".card { background: white; border: 1px solid #D3D1C7; border-radius: 12px; padding: 12px; }\n"
    ".card-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px; }\n"
    ".ticker { font-weight: 600; font-size: 15px; margin-right: 6px; }\n"
    ".name { font-size: 12px; color: #5F5E5A; }\n"
    ".pattern-title { font-size: 14px; font-weight: 500; margin-top: 4px; }\n"
    ".interval { font-size: 11px; color: #888780; font-weight: 400; }\n"
    ".status { font-size: 12px; font-weight: 600; margin-bottom: 6px; }\n"
    "img { width: 100%; border-radius: 8px; margin: 6px 0; display: block; }\n"
    ".metrics { display: flex; flex-wrap: wrap; gap: 10px; font-size: 12px; margin: 6px 0; }\n"
    ".metric { display: flex; flex-direction: column; }\n"
    ".metric span { color: #888780; font-size: 10px; }\n"
    ".metric strong { font-size: 13px; }\n"
    ".notes { font-size: 11px; color: #5F5E5A; margin-top: 4px; }\n"
    ".badge { font-size: 10px; padding: 2px 8px; border-radius: 10px; margin-left: 4px; }\n"
    ".badge.new { background: #C0DD97; color: #173404; }\n"
    ".badge.changed { background: #FAC775; color: #412402; }\n"
    ".badge.vol-ok { background: #9FE1CB; color: #04342C; }\n"
    ".badge.vol-weak { background: #F0997B; color: #4A1B0C; }\n"
)


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
        vol_note = '<span class="badge vol-ok">volum confirmat (' + str(p.get('volume_ratio')) + 'x medie)</span>'
    elif p.get('volume_confirmed') is False:
        vol_note = '<span class="badge vol-weak">volum slab (' + str(p.get('volume_ratio')) + 'x medie)</span>'

    img_html = ''
    if hit['chart_path']:
        img_html = '<img src="' + hit['chart_path'] + '" alt="' + hit['symbol'] + ' ' + p['type'] + '" loading="lazy">'

    invalid_line = ''
    if p.get('invalidation_price'):
        invalid_line = '<div class="metric"><span>Invalidare</span><strong>' + str(p['invalidation_price']) + '</strong></div>'

    parts = []
    parts.append('<div class="card">')
    parts.append('<div class="card-head"><div>')
    parts.append('<span class="ticker">' + hit['symbol'] + '</span>')
    parts.append('<span class="name">' + hit['name'] + '</span>')
    parts.append('</div><div class="badges">' + ''.join(badges) + '</div></div>')
    parts.append('<div class="pattern-title">' + p['type'] + ' <span class="interval">(' + hit['interval'] + ')</span></div>')
    parts.append('<div class="status" style="color:' + status_color + '">' + status_label + '</div>')
    parts.append(img_html)
    parts.append('<div class="metrics">')
    parts.append('<div class="metric"><span>Pret curent</span><strong>' + str(hit['last_price']) + '</strong></div>')
    parts.append('<div class="metric"><span>Trigger</span><strong>' + str(p['trigger_price']) + '</strong></div>')
    parts.append(invalid_line)
    parts.append('<div class="metric"><span>Calitate</span><strong>' + str(p['quality_score']) + '/100</strong></div>')
    parts.append('</div>')
    parts.append('<div class="notes">' + p['notes'] + ' ' + vol_note + '</div>')
    parts.append('</div>')
    return ''.join(parts)


def _section(title, hits):
    if not hits:
        return '<h2>' + title + '</h2><p class="empty">Niciun hit.</p>'
    cards = ''.join(_pattern_card(h) for h in hits)
    return '<h2>' + title + ' (' + str(len(hits)) + ')</h2><div class="grid">' + cards + '</div>'


def generate_report(all_hits, errors, outdir='docs', interval='1d'):
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    new_or_changed = [h for h in all_hits if h['is_new'] or h['status_changed']]
    confirmed = [h for h in all_hits if h['pattern']['status'] == 'confirmed']
    forming = [h for h in all_hits if h['pattern']['status'] == 'forming']

    new_or_changed.sort(key=lambda h: -h['pattern']['quality_score'])
    confirmed.sort(key=lambda h: -h['pattern']['quality_score'])
    forming.sort(key=lambda h: -h['pattern']['quality_score'])

    body_parts = []
    body_parts.append('<h1>Chart Pattern Scout</h1>')
    body_parts.append('<div class="meta">Ultima scanare: ' + now + ' - interval ' + interval + ' - ' + str(len(errors)) + ' tickere esuate la descarcare</div>')
    body_parts.append(_section('Nou / schimbat azi', new_or_changed))
    body_parts.append(_section('Toate pattern-urile confirmate', confirmed))
    body_parts.append(_section('In formare (watch)', forming))
    body = ''.join(body_parts)

    html_parts = []
    html_parts.append('<!DOCTYPE html>')
    html_parts.append('<html lang="ro">')
    html_parts.append('<head>')
    html_parts.append('<meta charset="utf-8">')
    html_parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    html_parts.append('<title>Chart Pattern Scout</title>')
    html_parts.append('<style>')
    html_parts.append(CSS)
    html_parts.append('</style>')
    html_parts.append('</head>')
    html_parts.append('<body>')
    html_parts.append(body)
    html_parts.append('</body>')
    html_parts.append('</html>')
    html = ''.join(html_parts)

    out_path = os.path.join(outdir, 'index.html')
    with open(out_path, 'w') as f:
        f.write(html)
    return out_path
