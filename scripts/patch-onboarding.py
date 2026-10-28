from pathlib import Path

p=Path('src/main.jsx')
s=p.read_text()

component='''function Onboarding({onStart}){return <div className="onboarding-backdrop"><div className="onboarding-card"><div className="onboarding-brand"><div className="mark">L</div><div><b>LookLiP</b><span>FINANCE</span></div></div><div className="onboarding-eyebrow">Conheça o LookLiP Finance</div><h1>Seu dinheiro. Sua visão. Suas decisões.</h1><p className="onboarding-intro">Uma visão simples e inteligente para organizar sua vida financeira e transformar números em decisões.</p><div className="onboarding-grid"><div><strong>↔ Fluxo</strong><span>Entradas, despesas e saldo mês a mês.</span></div><div><strong>● Prestadores</strong><span>Controle valores e impacto no seu fluxo.</span></div><div><strong>▣ Transferências</strong><span>Organize movimentações e compromissos.</span></div><div><strong>◫ Budget</strong><span>Planeje gastos e acompanhe o realizado.</span></div><div><strong>◇ Dash</strong><span>Indicadores, tendências e prioridades de ação.</span></div></div><button className="primary onboarding-start" onClick={onStart}>Começar a usar</button><small>Você poderá voltar ao app normalmente depois desta apresentação.</small></div></div>}\n'''

if 'function Onboarding({' not in s:
    marker='function Splash(){'
    if marker not in s: raise SystemExit('Splash marker not found')
    s=s.replace(marker,component+marker,1)

old="if(session===undefined||!hasLoaded)return <Splash/>;if(!session&&!hasSupabaseConfig()){}else if(!session&&hasSupabaseConfig())return <Login/>;const updateFlux="
new='''if(session===undefined||!hasLoaded)return <Splash/>;if(!session&&!hasSupabaseConfig()){}else if(!session&&hasSupabaseConfig())return <Login/>;const onboardingKey=session?.user?.id?`looklip-onboarding:${session.user.id}`:"looklip-onboarding";const [showOnboarding,setShowOnboarding]=useState(()=>{try{return localStorage.getItem(onboardingKey)!=='1'}catch{return true}});const finishOnboarding=()=>{try{localStorage.setItem(onboardingKey,'1')}catch{};setShowOnboarding(false)};if(showOnboarding)return <><div className="app" style={{visibility:'hidden'}}></div><Onboarding onStart={finishOnboarding}/></>;const updateFlux='''
if old not in s: raise SystemExit('App insertion marker not found')
s=s.replace(old,new,1)
p.write_text(s)
print('Onboarding applied')
