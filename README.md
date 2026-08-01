# MyFinance

Aplicativo desktop de **controle financeiro pessoal**, simples e offline.

Gerencie contas, categorias e lançamentos, acompanhe o saldo no dashboard e filtre relatórios — tudo localmente no seu computador.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.6+-green)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Funcionalidades

- **Autenticação** — login e criação de conta (senha com hash SHA-256)
- **Dashboard** — saldo total, receitas e despesas do mês, contas ativas e últimos lançamentos
- **Contas bancárias** — CRUD com soft delete e atualização de saldo
- **Categorias** — receitas e despesas, com cor opcional
- **Movimentações** — lançamentos vinculados a conta e categoria; saldo atualizado automaticamente
- **Relatórios** — filtros por período, tipo, conta e categoria, com totais do período
- **Temas** — claro e escuro, com troca em tempo real (sem reiniciar)
- **Interface** — sidebar de navegação, layout responsivo e tema QSS

## Tecnologias

| Camada | Tecnologia |
|--------|------------|
| Interface | PySide6 (Qt 6) + arquivos `.ui` |
| Persistência | SQLite (SQL puro, sem ORM) |
| Estilo | QSS (temas dark e light) |
| Linguagem | Python 3.10+ |

## Arquitetura

O projeto segue **arquitetura em camadas**:

```
main.py          → ponto de entrada
app.py           → janela principal e navegação entre login/main
ui/              → layouts Qt Designer (.ui)
views/           → lógica de interface e sinais
controllers/     → fluxo e orquestração
services/        → regras de negócio e CRUD
models/          → entidades (dataclasses)
database/        → SQLite (DatabaseManager)
config/          → settings, temas e preferências
resources/       → ícones e estilos (.qss)
```

**Regras:**
- SQL apenas em `database/`
- Navegação centralizada em `App`
- Views não acessam o banco diretamente
- Services não conhecem widgets

## Estrutura de pastas

```
MyFinance/
├── main.py
├── app.py
├── requirements.txt
├── config/
│   └── settings.py
├── database/
│   └── database_manager.py
├── models/
├── services/
├── controllers/
├── views/
├── ui/
├── resources/
│   ├── icons/
│   └── styles/
│       ├── dark.qss
│       └── light.qss
└── data/                 # criado em runtime (banco e preferências)
```

## Pré-requisitos

- Python **3.10** ou superior
- pip

## Instalação

```bash
git clone https://github.com/Wedson-Junior/MyFinance.git
cd MyFinance

python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

## Execução

```bash
python main.py
```

Na primeira execução:
1. O banco SQLite é criado em `data/myfinance.db`
2. Crie uma conta na tela de login
3. Cadastre contas e categorias antes de lançar movimentações

## Uso rápido

1. **Login** — entre ou crie um usuário  
2. **Contas** — cadastre suas contas bancárias  
3. **Categorias** — crie categorias de receita e despesa  
4. **Movimentações** — registre lançamentos  
5. **Dashboard** — veja o resumo financeiro  
6. **Relatórios** — filtre por data, tipo, conta ou categoria  
7. **Configurações** — troque entre tema escuro e claro  

## Temas

- **Escuro** (padrão) e **Claro**
- Preferência salva em `data/preferences.json`
- Troca imediata em **Configurações → Tema** (sem reiniciar o app)

## Banco de dados

Tabelas criadas automaticamente:

| Tabela | Descrição |
|--------|-----------|
| `users` | Usuários e senha hash |
| `bank_accounts` | Contas e saldos |
| `categories` | Categorias (income / expense) |
| `transactions` | Lançamentos |

O diretório `data/` e os arquivos `*.db` estão no `.gitignore`.

## Desenvolvimento

Convenções do projeto:

- Sem comentários no código
- Nomes de variáveis e classes em **inglês**
- Type hints
- Uma classe principal por arquivo
- UI separada em arquivos `.ui`

## Roadmap

O desenvolvimento seguiu 12 steps (estrutura → polish).  
Detalhes em [`roadmap.MD`](roadmap.MD).

## Licença

Este projeto está sob a licença [MIT](LICENSE).

## Autor

[Wedson Junior](https://github.com/Wedson-Junior)
