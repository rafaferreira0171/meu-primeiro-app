from pathlib import Path
import re

p=Path('src/main.jsx')
s=p.read_text()

component='''function Onboarding({onStart}){return <div className="onboarding-backdrop"><div className="onboarding-card"><div className="onboarding-brand"><div className="mark">L</div><div><b>LookLiP</b><span>FINANCE</span></div></div><div className="onboarding-eyebrow">Conheça o LookLiP Finance</div><h1>Seu dinheiro. Sua visão. Suas decisões.</h1><p className="onboarding-intro">Uma visão simples e inteligente para organizar sua vida financeira e transformar números em decisões.</p><div className="onboarding-grid"><div><strong>↔ Fluxo</strong><span>Entradas, despesas e saldo mês a mês.</span></div><div><strong>● Prestadores</strong><span>Controle valores e impacto no seu fluxo.</span></div><div><strong>▣ Transferências</strong><span>Organize movimentações e compromissos.</span></div><div><strong>◫ Budget</strong><span>Planeje gastos e acompanhe o realizado.</span></div><div><strong>◇ Dash</strong><span>Indicadores, tendências e prioridades de ação.</span></div></div><button className="primary onboarding-start" onClick={onStart}>Começar a usar</button><small>Você poderá voltar ao app normalmente depois desta apresentação.</small></div></div>}\n'''

if 'function Onboarding({' not in s:
    marker='function Splash(){'
    if marker not in s: raise SystemExit('Splash marker not found')
    s=s.replace(marker,component+marker,1)

old_prefix="function App(){const{data,save,busy,error,setError,hasLoaded}=useFinance(),[tab,setTab]=useState('fluxo'),[month,setMonth]=useState(currentMonth()),[session,setSession]=useState(undefined),[confirm,setConfirm]=useState(null);"
if 'const [showOnboarding,setShowOnboarding]=useState(false)' not in s:
    if old_prefix not in s: raise SystemExit('App hook insertion marker not found')
    new_prefix="function App(){const{data,save,busy,error,setError,hasLoaded}=useFinance(),[tab,setTab]=useState('fluxo'),[month,setMonth]=useState(currentMonth()),[session,setSession]=useState(undefined),[confirm,setConfirm]=useState(null),[showOnboarding,setShowOnboarding]=useState(false);"
    s=s.replace(old_prefix,new_prefix,1)
    old_effect="useEffect(()=>{let active=true;getSession().then(s=>{if(active)setSession(s)}).catch(()=>{if(active)setSession(null)});const s=onAuthStateChange(setSession);return()=>{active=false;s.data.subscription.unsubscribe()}},[]);"
    new_effect=old_effect+"useEffect(()=>{if(!session)return;try{setShowOnboarding(localStorage.getItem(`looklip-onboarding:${session.user.id}`)!=='1')}catch{setShowOnboarding(true)}},[session?.user?.id]);"
    if old_effect not in s: raise SystemExit('Auth effect marker not found')
    s=s.replace(old_effect,new_effect,1)

if 'const finishOnboarding=()=>{try{localStorage.setItem(onboardingKey' not in s:
    marker='const updateFlux=p=>save('
    idx=s.find(marker)
    if idx<0: raise SystemExit('Onboarding render marker not found')
    prefix='const finishOnboarding=()=>{try{localStorage.setItem(onboardingKey,\'1\')}catch{};setShowOnboarding(false)};if(showOnboarding)return <><div className="app" style={{visibility:\'hidden\'}}></div><Onboarding onStart={finishOnboarding}/>;'
    # close fragment before the existing updateFlux declaration
    s=s[:idx]+prefix+s[idx:]

p.write_text(s)
print('Onboarding applied with hooks before early returns and after Fluxo transforms')
