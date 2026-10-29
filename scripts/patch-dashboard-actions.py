from pathlib import Path
import re

p = Path('src/main.jsx')
s = p.read_text()

new_actions = r'''function DashActions({data,month,mode='fluxo'}){const refMonth=month||currentMonth();if(mode==='budget'){const accounts=data.budgetAccounts.filter(a=>a.month===refMonth&&a.ativo!==false).map(a=>{const spent=data.gastos.filter(g=>g.month===refMonth&&g.budget_account_id===a.id).reduce((s,g)=>s+Number(g.valor||0),0);const budget=Number(a.budget||0);return {...a,spent,budget,remaining:budget-spent,pct:budget?spent/budget*100:0}}).sort((a,b)=>b.pct-a.pct),over=accounts.filter(a=>a.remaining<0),top=accounts[0],totalBudget=accounts.reduce((s,a)=>s+a.budget,0),totalSpent=accounts.reduce((s,a)=>s+a.spent,0),util=totalBudget?totalSpent/totalBudget*100:0;const actions=[];if(over.length)actions.push({p:'Alta',title:'Corrigir contas acima do budget',text:`${over.length} conta(s) ultrapassaram o limite. Priorize ${over[0].nome}.`,cls:'danger'});else if(util>=80)actions.push({p:'Alta',title:'Desacelerar o consumo',text:`O budget já está em ${util.toFixed(1)}%. Evite novas despesas não essenciais.`,cls:'warning'});else actions.push({p:'Baixa',title:'Budget sob controle',text:`${util.toFixed(1)}% utilizado. Mantenha o ritmo atual de consumo.`,cls:'ok'});if(top&&top.pct>=80)actions.push({p:'Média',title:`Monitorar ${top.nome}`,text:`É a conta com maior utilização, em ${top.pct.toFixed(0)}%.`,cls:top.pct>=100?'danger':'warning'});if(totalBudget&&totalSpent<totalBudget)actions.push({p:'Média',title:'Preservar a folga',text:`Ainda há ${BRL(totalBudget-totalSpent)} disponíveis no budget do mês.`,cls:'ok'});return <Section title="Prioridades de ação"><div className="action-list">{actions.slice(0,3).map((a,i)=><div className={`action-item ${a.cls}`} key={a.title}><span className="action-priority">{a.p}</span><div><b>{a.title}</b><small>{a.text}</small></div><strong>{i+1}</strong></div>)}</div></Section>}const months=planningMonths(refMonth,12),rows=months.map(m=>{const f=data.fluxo.find(x=>x.month===m)||{},prest=data.prestadores.filter(x=>x.month===m&&x.ativo!==false),entradas=data.entradas.filter(x=>x.month===m&&x.ativo!==false),despesas=data.despesas.filter(x=>x.month===m&&x.ativo!==false);return {m,...calcFluxoMonth(f,prest,despesas,entradas)}}),current=rows[0]||{entries:0,expenses:0,balance:0},futureNegative=rows.slice(1).filter(x=>x.balance<0),commitment=current.entries?current.expenses/current.entries*100:0,expenseMap=new Map(),f=data.fluxo.find(x=>x.month===refMonth)||{};FLUXO_FIELDS.forEach(([k,l])=>{const v=Number(f[k]||0);if(v)expenseMap.set(l,v)});data.despesas.filter(x=>x.month===refMonth&&x.ativo!==false).forEach(x=>{const v=Number(x.valor||0);expenseMap.set(x.nome,(expenseMap.get(x.nome)||0)+v)});if(current.employeeTotal)expenseMap.set('Prestadores de Serviço',current.employeeTotal);const top=[...expenseMap.entries()].sort((a,b)=>b[1]-a[1])[0],topShare=current.expenses&&top?top[1]/current.expenses*100:0,actions=[];if(current.balance<0)actions.push({p:'Alta',title:'Proteger o caixa agora',text:`O mês está ${BRL(Math.abs(current.balance))} negativo. Revise primeiro as maiores despesas.`,cls:'danger'});else if(commitment>=80)actions.push({p:'Alta',title:'Reduzir a pressão do caixa',text:`${commitment.toFixed(1)}% das entradas já estão comprometidas neste mês.`,cls:'warning'});else actions.push({p:'Baixa',title:'Manter geração de caixa',text:`O mês fecha com ${BRL(current.balance)} de saldo positivo.`,cls:'ok'});if(futureNegative.length){const w=futureNegative.sort((a,b)=>a.balance-b.balance)[0];actions.push({p:'Alta',title:`Planejar ${w.m}`,text:`Há uma projeção de ${BRL(Math.abs(w.balance))} negativos. Antecipe ajustes antes desse mês.`,cls:'danger'})}else actions.push({p:'Média',title:'Proteger os meses de menor folga',text:'Nenhum mês futuro está negativo, mas acompanhe os menores saldos projetados.',cls:'ok'});if(top&&topShare>=30)actions.push({p:'Média',title:`Atacar ${top[0]}`,text:`A maior despesa representa ${topShare.toFixed(1)}% do total do mês. É o principal ponto para revisão.`,cls:'warning'});return <Section title="Prioridades de ação"><div className="action-list">{actions.slice(0,3).map((a,i)=><div className={`action-item ${a.cls}`} key={a.title}><span className="action-priority">{a.p}</span><div><b>{a.title}</b><small>{a.text}</small></div><strong>{i+1}</strong></div>)}</div></Section>}
'''

if 'function DashActions(' not in s:
    marker = 'function DashBudget('
    idx = s.find(marker)
    if idx < 0:
        raise SystemExit('DashBudget marker not found')
    s = s[:idx] + new_actions + s[idx:]

needle = '</Section><div className="grid2"><Section title="Pressão das despesas">'
if '<DashActions data={data} month={refMonth} mode="fluxo"/>' not in s:
    pos = s.find(needle)
    if pos < 0:
        raise SystemExit('Fluxo dashboard insertion point not found')
    s = s[:pos] + '</Section><DashActions data={data} month={refMonth} mode="fluxo"/><div className="grid2"><Section title="Pressão das despesas">' + s[pos+len(needle):]

if '<DashActions data={data} month={refMonth} mode="budget"/>' not in s:
    pattern = r'(function DashBudget\([\s\S]*?<Section title="Leitura do budget">[\s\S]*?</Section>)(</div>})'
    s, n = re.subn(pattern, r'\1<DashActions data={data} month={refMonth} mode="budget"/>\2', s, count=1)
    if n != 1:
        raise SystemExit('Budget dashboard insertion point not found')

p.write_text(s)

css_path = Path('src/styles.css')
css = css_path.read_text() if css_path.exists() else ''
extra = r'''
/* Dashboard action priorities */
.action-list{display:grid;gap:9px}.action-item{display:grid;grid-template-columns:auto 1fr auto;gap:11px;align-items:center;border:1px solid #e9edf2;border-radius:13px;padding:12px 13px;background:#fbfcfd}.action-item>div{min-width:0}.action-item>b,.action-item div>b{font-size:12px;line-height:1.25}.action-item small{display:block;margin-top:4px;color:#697384;font-size:10px;line-height:1.35}.action-priority{font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:.06em;padding:5px 7px;border-radius:7px;background:#eef2f6;color:#697384}.action-item>strong{font-size:18px;color:#d1d7df;font-weight:800}.action-item.warning{background:#fffaf1;border-color:#f0dfbd}.action-item.warning .action-priority{background:#fff0cf;color:#9a6a14}.action-item.danger{background:#fff7f7;border-color:#f1cccc}.action-item.danger .action-priority{background:#fde1e1;color:#a63a3a}.action-item.ok .action-priority{background:#e9f7ef;color:#317d55}
@media(max-width:800px){.action-item{grid-template-columns:auto 1fr auto;padding:11px}.action-item small{font-size:9px}.action-item>strong{font-size:16px}}
'''
if '/* Dashboard action priorities */' not in css:
    css += extra
    css_path.write_text(css)
