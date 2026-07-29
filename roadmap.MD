# CLAUDE.md

# Projeto PySide6

Sempre siga esta sequência antes de escrever qualquer código.

---

# STEP 1 — Entenda a Arquitetura

Este projeto utiliza arquitetura em camadas.

Nunca ignore esta estrutura.

```
MeuProjeto/
│
├── main.py
├── app.py
│
├── ui/
├── views/
├── controllers/
├── models/
├── services/
├── database/
├── resources/
├── utils/
└── config/
```

---

# STEP 2 — Descubra onde o código pertence

Antes de criar qualquer arquivo, responda:

A funcionalidade pertence a:

- Interface?
- Controller?
- Service?
- Model?
- Database?
- Utils?
- Config?

Nunca coloque código na primeira pasta que encontrar.

---

# STEP 3 — Respeite a responsabilidade de cada camada

## main.py

Somente:

- criar QApplication
- carregar tema
- iniciar App
- executar app.exec()

Nunca adicionar regras de negócio.

---

## app.py

Responsável por:

- navegação
- gerenciamento de telas
- estado global
- compartilhamento de serviços

Nenhuma View deve abrir outra View diretamente.

---

## ui/

Contém apenas arquivos .ui.

Nunca adicionar lógica.

---

## views/

Responsável apenas por:

- carregar .ui
- acessar widgets
- atualizar interface
- emitir sinais

Nunca colocar:

- SQL
- autenticação
- HTTP
- regras de negócio

---

## controllers/

Responsável por:

- responder eventos
- validar entradas
- chamar Services
- atualizar Views

Toda lógica da interface fica aqui.

---

## services/

Responsável por:

- APIs
- autenticação
- JWT
- OAuth
- PDF
- arquivos
- e-mails

Nunca acessar widgets.

---

## models/

Representam entidades da aplicação.

Exemplos:

- User
- Product
- Order

---

## database/

Todo acesso ao banco passa por esta camada.

Nenhuma outra camada executa SQL.

---

## resources/

```
resources/
    icons/
    images/
    styles/
```

Nunca misturar arquivos.

---

## utils/

Funções reutilizáveis.

---

## config/

Constantes e configurações.

---

# STEP 4 — Fluxo obrigatório

Sempre seguir:

```
main.py

↓

QApplication

↓

App

↓

View

↓

Controller

↓

Service

↓

Database
```

Nunca inverter esse fluxo.

---

# STEP 5 — Navegação

Nunca faça:

```python
DashboardWindow().show()
```

Sempre:

```python
self.app.show_dashboard()
```

ou

```python
self.navigate.emit("dashboard")
```

Toda navegação passa pelo App.

---

# STEP 6 — Organização dos arquivos

Uma classe principal por arquivo.

Exemplo:

```
views/

login_view.py

dashboard_view.py
```

Evite arquivos grandes.

---

# STEP 7 — Interface

Sempre utilizar:

- Qt Designer
- arquivos .ui

Somente criar interface via código quando solicitado.

---

# STEP 8 — Estilos

Sempre utilizar:

```
resources/styles/
```

Arquivos:

```
.qss
```

Nunca escrever grandes blocos de CSS no Python.

---

# STEP 9 — Recursos

Ícones:

```
resources/icons/
```

Imagens:

```
resources/images/
```

QSS:

```
resources/styles/
```

---

# STEP 10 — Banco de Dados

Todo SQL deve passar pela camada:

```
database/
```

Views e Controllers nunca executam SQL.

---

# STEP 11 — Services

Services:

Recebem dados.

Processam.

Retornam resultados.

Nunca conhecem Views.

---

# STEP 12 — Controllers

Toda lógica de clique.

Toda comunicação entre View e Service.

Nunca colocar regras de negócio dentro da View.

---

# STEP 13 — Convenções

## Classes

```
LoginView

DashboardController

UserService

DatabaseManager
```

## Arquivos

```
login_view.py

dashboard_controller.py

user_service.py

database_manager.py
```

## Métodos

```
load_data()

save_user()

authenticate()

show_dashboard()
```

---

# STEP 14 — Boas práticas

Sempre:

- utilizar POO
- utilizar SOLID quando possível
- criar funções pequenas
- reutilizar código
- evitar duplicação
- utilizar nomes descritivos
- utilizar type hints
- utilizar docstrings quando agregarem valor

---

# STEP 15 — Antes de finalizar

Verifique:

- A arquitetura foi respeitada?
- O código ficou desacoplado?
- Existe duplicação?
- O arquivo foi colocado na pasta correta?
- A View possui apenas interface?
- O Controller possui apenas lógica de interface?
- O Service possui apenas regras de negócio?
- O Database ficou isolado?
- Os recursos foram colocados em resources?
- O código é escalável?

Se alguma resposta for "não", reorganize antes de finalizar.

---

# Objetivo Final

Todo código produzido deve ser:

- organizado
- modular
- desacoplado
- reutilizável
- escalável
- fácil de manter
- preparado para crescimento futuro

Estas etapas têm prioridade sobre qualquer geração de código.