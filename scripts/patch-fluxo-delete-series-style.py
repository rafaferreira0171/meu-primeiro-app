from pathlib import Path

p = Path('src/styles.css')
s = p.read_text()
marker = '.series-row{display:grid;grid-template-columns:28px minmax(0,1fr) 125px;align-items:center;gap:8px}.series-row .series-delete{width:28px;height:28px;border:0;border-radius:8px;background:#fff0f0;color:var(--danger);font-size:18px;line-height:1;cursor:pointer;padding:0;display:grid;place-items:center}.series-row .series-delete:hover{background:#ffe2e2}.series-row input{width:125px;min-width:0}'
if '.series-row{' in s:
    print('Fluxo delete button styles already present')
else:
    s += marker
    p.write_text(s)
    print('Fluxo delete button styles added.')
