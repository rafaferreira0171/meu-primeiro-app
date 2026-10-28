from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()
old = "const update=(id,p)=>save({...data,prestadores:data.prestadores.map(x=>x.id===id?{...x,...p}:x)})"
new = "const update=(id,p)=>{const current=data.prestadores.find(x=>x.id===id);if(!current)return;const sid=current.prestador_id||current.id;save({...data,prestadores:data.prestadores.map(x=>(x.prestador_id||x.id)===sid&&x.month>=current.month?{...x,...p}:x)})}"
if old in s:
    s = s.replace(old,new,1)
    print('Provider edits now propagate from the edited month forward')
else:
    print('Provider future propagation already applied; no additional patch needed')
p.write_text(s)
