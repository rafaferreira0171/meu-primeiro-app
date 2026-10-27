from pathlib import Path

path = Path('src/main.jsx')
s = path.read_text(encoding='utf-8')
replacements = [
    (
        "function App(){const{data,save,busy,error,setError,hasLoaded}=useFinance(),[tab,setTab]=useState('fluxo'),[month,setMonth]=useState(currentMonth()),[session,setSession]=useState(undefined);",
        "function App(){const{data,save,busy,error,setError,hasLoaded}=useFinance(),[tab,setTab]=useState('fluxo'),[month,setMonth]=useState(currentMonth()),[session,setSession]=useState(undefined),[confirm,setConfirm]=useState(null);"
    ),
    (
        "const stopSeries=(field,id)=>{if(!confirm('Encerrar a partir do próximo mês? O histórico será preservado.'))return;const next=addMonths(month,1);save({...data,[field]:data[field].map(x=>(x.series_id||x.id)===id&&x.month>=next?{...x,ativo:false}:x)})};",
        "const stopSeries=(field,id)=>{setConfirm({title:'Encerrar recorrência',message:'Encerrar a partir do próximo mês? O histórico será preservado.',onConfirm:()=>{const next=addMonths(month,1);save({...data,[field]:data[field].map(x=>(x.series_id||x.id)===id&&x.month>=next?{...x,ativo:false}:x)});setConfirm(null)}})};"
    ),
    (
        "{tab==='budget'&&<Budget data={data} save={save}/>}",
        "{tab==='budget'&&<Budget data={data} save={save} month={month} setMonth={setMonth}/>}"
    ),
    (
        "</main></div>}\nfunction Splash()",
        "</main>{confirm&&<Modal title={confirm.title} onClose={()=>setConfirm(null)} onSave={confirm.onConfirm} saveLabel=\"Encerrar\"><p className=\"helper\">{confirm.message}</p></Modal>}</div>}\nfunction Splash()"
    ),
    (
        "<MonthSelect month={month} setMonth={()=>{}} months={data.fluxo.map(x=>x.month)}/><button className=\"primary\" onClick={()=>setModal({type:'prestador'})}>+ Prestador</button>",
        "<MonthSelect month={month} setMonth={setMonth} months={data.fluxo.map(x=>x.month)}/><button className=\"primary\" onClick={()=>setModal({type:'prestador'})}>+ Prestador</button>"
    ),
    (
        "function Budget({data,save}){const month=currentMonth(),accounts=calcBudgetMonth(data.gastos,month,data.budgetAccounts),",
        "function Budget({data,save,month,setMonth}){const accounts=calcBudgetMonth(data.gastos,month,data.budgetAccounts),"
    ),
    (
        "<div className=\"toolbar\"><span className=\"toolbar-title\">Budget · {month}</span><button className=\"primary\" onClick={()=>setModal({type:'account'})}>+ Nova categoria</button></div>",
        "<div className=\"toolbar\"><MonthSelect month={month} setMonth={setMonth} months={data.fluxo.map(x=>x.month)}/><button className=\"primary\" onClick={()=>setModal({type:'account'})}>+ Nova categoria</button></div>"
    ),
]
for old, new in replacements:
    if old not in s:
        raise SystemExit(f'pattern not found: {old[:100]}')
    s = s.replace(old, new, 1)
path.write_text(s, encoding='utf-8')
print('patched product flows')
