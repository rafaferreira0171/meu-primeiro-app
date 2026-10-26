# LookLiP Finance

Aplicativo independente de inteligência financeira pessoal, reconstruído a partir do antigo projeto do LookLiP Finance no Base44.

## Módulos
- **Fluxo** — entradas configuráveis, despesas fixas, contas personalizadas e cálculos automáticos.
- **Prestadores** — cards individuais por prestador, com salário, dias úteis, passagens e total geral.
- **Transferências** — cards por pessoa/mês, permitindo selecionar quais contas compõem cada transferência.
- **Entradas x Budget** — lançamentos de Mercado, Gasolina e Avulso, com ajustes e histórico.
- **LookLiP Dash** — visão executiva com médias, comprometimento de renda, composição, evolução e leitura das transferências derivadas.

## Regra importante das transferências
Transferências são uma visão derivada de despesas já cadastradas. Os valores selecionados em uma transferência **não são somados novamente ao Dash como despesa**, evitando dupla contagem.

## Arquitetura atual
- React + Vite.
- Autenticação preparada para Supabase Auth.
- Banco independente preparado para Supabase, com RLS por usuário.
- Camada de dados com fallback para `localStorage` quando o Supabase não está configurado.
- Entradas, prestadores e transferências configuráveis por usuário.
- Build e sincronização preparados para a futura publicação em iPhone/Android.

## Configuração do backend
Crie um projeto no Supabase e aplique `supabase/schema.sql`. Depois configure:

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

Sem essas variáveis, o aplicativo continua operando localmente no navegador para desenvolvimento.

## Estado do projeto
A base independente está em evolução de produto. O próximo foco é refinar o Dash, identidade visual, automações e experiência mobile antes do empacotamento final para iPhone/Android.

O projeto original do Base44 permanece preservado separadamente.
