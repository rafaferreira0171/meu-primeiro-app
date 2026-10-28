from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()

old_p = '<MonthSelect month={month} setMonth={setMonth} months={data.prestadores.map(x=>x.month)}/>'
new_p = '<MonthSelect month={month} setMonth={setMonth} months={MONTHS}/>'
if old_p in s:
    s = s.replace(old_p, new_p, 1)

old_t = '<MonthSelect month={month} setMonth={setMonth} months={data.transferencias.map(x=>x.month)}/>'
new_t = '<MonthSelect month={month} setMonth={setMonth} months={MONTHS}/>'
if old_t in s:
    s = s.replace(old_t, new_t, 1)

p.write_text(s)
print('Canonical month selector applied to Prestadores and Transferências')
