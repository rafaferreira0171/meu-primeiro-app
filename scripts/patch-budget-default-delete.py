from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()
start = s.find('function Budget(')
end = s.find('function Dash(', start)
if start < 0 or end < 0:
    raise SystemExit('Budget component not found')

old = s[start:end]
needle = "const update=(id,budget)=>save({...data,budgetAccounts:data.budgetAccounts.map(a=>a.id===id?{...a,budget}:a)})"
if needle not in old:
    raise SystemExit('Budget update function not found')
if 'const removeAccount=' not in old:
    old = old.replace(needle, needle + ";const removeAccount=id=>save({...data,budgetAccounts:data.budgetAccounts.map(a=>a.id===id?{...a,ativo:false}:a)})")

# Add Excluir next to the existing Editar button, regardless of the exact prompt formatting.
if 'onClick={()=>removeAccount(a.id)}' not in old:
    marker = "</button></div><div className=\"budget-values\">"
    if marker not in old:
        raise SystemExit('Budget Editar button insertion point not found')
    old = old.replace(marker, "</button><button className=\"ghost danger\" onClick={()=>removeAccount(a.id)}>Excluir</button></div><div className=\"budget-values\">", 1)

s = s[:start] + old + s[end:]
p.write_text(s)
print('Budget: default and custom accounts now have a persistent Excluir action')
