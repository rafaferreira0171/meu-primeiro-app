from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()
old_ui = '<Row label=\\"50% Prestadores\\" value={fm.employeeHalf} auto/>'
new_ui = '<Row label=\\"Prestadores de Serviço\\" value={fm.employeeTotal} auto/>'
if old_ui in s:
    s = s.replace(old_ui, new_ui, 1)

f = Path('src/lib/finance.js')
s = f.read_text()
old = "export function calcFluxoMonth(fluxo,prestadores=[],despesas=[],entradas=[]){const entries=Number(fluxo?.salario||0)+Number(fluxo?.va||0)+entradas.reduce((s,x)=>s+Number(x.valor||0),0);const fixed=FLUXO_FIELDS.reduce((s,[k])=>s+Number(fluxo?.[k]||0),0);const custom=despesas.reduce((s,x)=>s+Number(x.valor||0),0);const employeeHalf=totalPrestadores(prestadores)/2;const expenses=fixed+custom+employeeHalf+AUTO_TAX;return{entries,expenses,balance:entries-expenses,employeeHalf,tax:AUTO_TAX}}"
new = "export function calcFluxoMonth(fluxo,prestadores=[],despesas=[],entradas=[]){const entries=Number(fluxo?.salario||0)+Number(fluxo?.va||0)+entradas.reduce((s,x)=>s+Number(x.valor||0),0);const fixed=FLUXO_FIELDS.reduce((s,[k])=>s+Number(fluxo?.[k]||0),0);const custom=despesas.reduce((s,x)=>s+Number(x.valor||0),0);const employeeTotal=totalPrestadores(prestadores);const expenses=fixed+custom+employeeTotal+AUTO_TAX;return{entries,expenses,balance:entries-expenses,employeeTotal,tax:AUTO_TAX}}"
if old in s:
    s = s.replace(old, new, 1)

p.write_text(s)
f.write_text(s)
print('Prestadores -> Fluxo patch checked')
