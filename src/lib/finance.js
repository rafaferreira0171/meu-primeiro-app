export const MONTHS = [
  '2026-11','2026-12','2027-01','2027-02','2027-03','2027-04','2027-05','2027-06',
  '2027-07','2027-08','2027-09','2027-10','2027-11','2027-12'
]

export const FLUXO_FIELDS = [
  ['condominio','Condomínio'],['iptu','IPTU'],['gas','Gás'],['internet','Internet'],['luz','Luz'],
  ['mercado','Mercado'],['combustivel','Combustível'],['seguro_carro','Seguro carro'],['convenio','Convênio'],
  ['cartao','Cartão'],['celular','Celular'],['cabelo','Cabelo'],['academia','Academia'],['contabilidade','Contabilidade'],
  ['pernambucanas','Pernambucanas'],['assin_chat','Assin. Chat'],['assin_apple','Assin. Apple'],
  ['assin_ifood','Assin. iFood'],['assin_uber','Assin. Uber'],['outros','Outros']
]

export const AUTO_TAX = 360

export function totalPrestador(p) {
  if (!p) return 0
  return Number(p.salario || 0) + Number(p.dias_uteis || 0) * (Number(p.passagem_scs || 0) + Number(p.passagem_sp || 0))
}

export function totalPrestadores(list = []) {
  return list.reduce((sum, p) => sum + totalPrestador(p), 0)
}

export function calcFluxoMonth(fluxo, prestadores = [], despesas = [], entradas = []) {
  const legacyEntries = Number(fluxo?.salario || 0) + Number(fluxo?.va || 0)
  const extraEntries = entradas.reduce((sum, item) => sum + Number(item.valor || 0), 0)
  const entries = legacyEntries + extraEntries
  const fixed = FLUXO_FIELDS.reduce((sum, [key]) => sum + Number(fluxo?.[key] || 0), 0)
  const custom = despesas.reduce((sum, item) => sum + Number(item.valor || 0), 0)
  const auto = totalPrestadores(prestadores) / 2 + AUTO_TAX
  const expenses = fixed + custom + auto
  return { entries, expenses, balance: entries - expenses, employeeHalf: totalPrestadores(prestadores) / 2, tax: AUTO_TAX }
}

export function calcPixMonth(fluxo, prestadores = []) {
  const employeeHalf = totalPrestadores(prestadores) / 2
  const convenio = Number(fluxo?.convenio || 0)
  return { employeeHalf, convenio, total: employeeHalf + convenio }
}

export function transferItemValue(item, fluxo, prestadores = [], despesas = []) {
  if (!item) return 0
  if (item.type === 'fluxo') return Number(fluxo?.[item.key] || 0)
  if (item.type === 'despesa') return Number(despesas.find(d => d.id === item.key)?.valor || 0)
  if (item.type === 'prestador_half') return totalPrestador(prestadores.find(p => p.id === item.key)) / 2
  return 0
}

export function calcTransfer(transfer, fluxo, prestadores = [], despesas = []) {
  return (transfer?.items || []).reduce((sum, item) => sum + transferItemValue(item, fluxo, prestadores, despesas), 0)
}

export function calcBudgetMonth(gastos, month) {
  const accounts = ['mercado','gasolina','avulso']
  return accounts.reduce((out, account) => {
    out[account] = gastos.filter(g => g.month === month && g.conta === account).reduce((sum, g) => sum + Number(g.valor || 0), 0)
    return out
  }, {})
}
