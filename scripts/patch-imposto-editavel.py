from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()

# Preserve the existing default tax value for new/planned months, while making it editable.
if 'imposto:360' not in s:
    s = s.replace('outros:153}', 'outros:153,imposto:360}')

# Migrate existing saved months that predate the editable tax field.
needle = "d.fluxo=d.fluxo.filter(x=>x.month>=d.startMonth);"
if needle in s and 'x.imposto===undefined' not in s:
    s = s.replace(needle, "d.fluxo.forEach(x=>{if(x.imposto===undefined)x.imposto=360});" + needle)

# Tax is no longer calculated/locked automatically: it is a normal editable Fluxo field.
s = s.replace('<Row label="Imposto" value={fm.tax} auto/>', '<Row label="Imposto" value={f.imposto} onChange={v=>updateFlux({imposto:v})}/>')
s = s.replace('Prestadores e imposto entram automaticamente. Encerrar preserva o histórico.', 'Prestadores são calculados automaticamente. Imposto é editável. Encerrar preserva o histórico.')

p.write_text(s)
print('Imposto is now an editable Fluxo field')
