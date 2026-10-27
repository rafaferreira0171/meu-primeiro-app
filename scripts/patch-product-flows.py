from pathlib import Path

# Main UI patch
path = Path('src/main.jsx')
s = path.read_text(encoding='utf-8')
main_replacements = [
    (
        "{tab==='prestadores'&&<Prestadores data={data} save={save} month={month}/>}",
        "{tab==='prestadores'&&<Prestadores data={data} save={save} month={month} setMonth={setMonth}/>}",
    ),
    (
        "function Prestadores({data,save,month}){",
        "function Prestadores({data,save,month,setMonth}){",
    ),
    (
        "passagem_scs:Number(scs)||0,passagem_sp:Number(sp)||0,ativo:true",
        "passagem_scs:Number(scs)||0,passagem_sp:Number(sp)||0,fluxo_percentual:50,ativo:true",
    ),
    (
        "{list.map(p=><div className=\"provider-row\" key={p.id}><div><b>{p.nome}</b><small>{p.dias_uteis} dias · {BRL(totalPrestador(p))}</small></div><strong>{BRL(totalPrestador(p))}</strong></div>)}",
        "{list.map(p=>{const total=totalPrestador(p),percent=Math.max(0,Math.min(100,Number(p.fluxo_percentual??50)));return <div className=\"provider-row\" key={p.id}><div><b>{p.nome}</b><small>{p.dias_uteis} dias · {BRL(total)}</small></div><div className=\"provider-total\"><label><span>% Fluxo</span><input inputMode=\"numeric\" type=\"number\" min=\"0\" max=\"100\" step=\"1\" value={percent} onChange={e=>save({...data,prestadores:data.prestadores.map(x=>x.id===p.id?{...x,fluxo_percentual:Math.max(0,Math.min(100,Number(e.target.value)||0))}:x)})}/></label><strong>{BRL(total*percent/100)}</strong><small>{BRL(total)} total</small></div></div>})}",
    ),
]
for old, new in main_replacements:
    if old in s:
        s = s.replace(old, new, 1)
path.write_text(s, encoding='utf-8')

# Finance calculation patch
path = Path('src/lib/finance.js')
s = path.read_text(encoding='utf-8')
finance_replacements = [
    (
        "export function totalPrestadores(list=[]){return list.reduce((s,p)=>s+totalPrestador(p),0)}",
        "export function fluxoPercentual(p){return Math.max(0,Math.min(100,Number(p?.fluxo_percentual??50)))}\nexport function totalPrestadorFluxo(p){return totalPrestador(p)*fluxoPercentual(p)/100}\nexport function totalPrestadores(list=[]){return list.reduce((s,p)=>s+totalPrestador(p),0)}\nexport function totalPrestadoresFluxo(list=[]){return list.reduce((s,p)=>s+totalPrestadorFluxo(p),0)}",
    ),
    (
        "const employeeTotal=totalPrestadores(prestadores);",
        "const employeeTotal=totalPrestadoresFluxo(prestadores);",
    ),
    (
        "if(item.type==='prestador_half'){const p=prestadores.find(x=>(x.prestador_id||x.id)===item.key);return totalPrestador(p)/2}",
        "if(item.type==='prestador_half'||item.type==='prestador_fluxo'){const p=prestadores.find(x=>(x.prestador_id||x.id)===item.key);return totalPrestadorFluxo(p)}",
    ),
]
for old, new in finance_replacements:
    if old not in s:
        raise SystemExit(f'finance pattern not found: {old[:100]}')
    s = s.replace(old, new, 1)
path.write_text(s, encoding='utf-8')
print('patched provider Flow percentage')
