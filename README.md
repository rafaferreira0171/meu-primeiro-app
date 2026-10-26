# LookLiP Finance

Aplicativo independente de controle financeiro pessoal, reconstruído a partir do antigo projeto do LookLiP Finance no Base44.

## Módulos
- **Fluxo** — entradas, despesas fixas, contas personalizadas e despesas automáticas.
- **Empregada** — salário, dias úteis e passagens por mês.
- **Pix** — cálculo de 50% do custo total da empregada + Convênio.
- **Entradas x Budget** — lançamentos de Mercado, Gasolina e Avulso, com ajustes e histórico.
- **LookLiP Dash** — visão executiva com médias, comprometimento de renda, composição e evolução mensal.

## Arquitetura atual
- React + Vite.
- Autenticação preparada para Supabase Auth.
- Banco independente preparado para Supabase, com RLS por usuário.
- Camada de dados com fallback para `localStorage` quando o Supabase não está configurado.
- IDs estáveis para lançamentos, permitindo sincronização e exclusão correta de registros.
- Build validado por GitHub Actions.

## Configuração do backend
Crie um projeto no Supabase e aplique `supabase/schema.sql`. Depois configure:

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

Sem essas variáveis, o aplicativo continua operando localmente no navegador para desenvolvimento.

## Estado do projeto
A base técnica independente está funcional e em fase de validação/refinamento antes da etapa de melhorias de produto. A migração dos dados históricos do Base44 e a publicação como aplicativo iPhone/Android ficam para uma etapa posterior.

O projeto original do Base44 permanece preservado separadamente.
