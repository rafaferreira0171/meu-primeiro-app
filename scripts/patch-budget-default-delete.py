from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()
start = s.find('function Budget(')
end = s.find('function Dash(', start)
if start < 0 or end < 0:
    raise SystemExit('Budget component not found')

old = s[start:end]
# Keep the existing Budget implementation, adding a soft-delete action to every account.
needle = "const update=(id,budget)=>save({...data,budgetAccounts:data.budgetAccounts.map(a=>a.id===id?{...a,budget}:a)})"
if needle not in old:
    raise SystemExit('Budget update function not found')
old = old.replace(needle, needle + ";const removeAccount=id=>save({...data,budgetAccounts:data.budgetAccounts.map(a=>a.id===id?{...a,ativo:false}:a)})")
old = old.replace("<button className=\"ghost\" onClick={()=>{const v=prompt('Novo budget',a.budget);if(v!==null)update(a.id,Number(v.replace(',','.')||0))}}>Editar</button>", "<button className=\"ghost\" onClick={()=>{const v=prompt('Novo budget',a.budget);if(v!==null)update(a.id,Number(v.replace(',','.')||0))}}>Editar</button><button className=\"ghost danger\" onClick={()=>removeAccount(a.id)}>Excluir</button>")

s = s[:start] + old + s[end:]
p.write_text(s)
print('Budget: default and custom accounts now have an Excluir action')
