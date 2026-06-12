# 🏦 Banco Python

Sistema bancário de terminal desenvolvido em Python com foco em **Programação Orientada a Objetos**, boas práticas e organização de código. Projeto de portfólio para demonstração de conceitos como herança, polimorfismo, encapsulamento e abstração.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Concluído-brightgreen)
![Testes](https://img.shields.io/badge/Testes-41%2F41%20✓-brightgreen)
![Linhas](https://img.shields.io/badge/Linhas%20de%20código-1.300%2B-informational)

---

## 📋 Índice

- [Sobre o projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Como executar](#-como-executar)
- [Arquitetura](#-arquitetura)
- [Conceitos de POO aplicados](#-conceitos-de-poo-aplicados)
- [Estrutura do projeto](#-estrutura-do-projeto)
- [Executar os testes](#-executar-os-testes)
- [Melhorias futuras](#-melhorias-futuras)
- [Tecnologias](#-tecnologias)

---

## 💡 Sobre o projeto

Este projeto simula as operações essenciais de um banco real via terminal. Foi desenvolvido como projeto de estudos para consolidar conceitos de **POO em Python**, com atenção especial a:

- Organização e clareza de código
- Separação de responsabilidades entre classes
- Tratamento robusto de erros com exceções customizadas
- Validações de regras de negócio reais (limite de saque, saques diários, CPF, senha)
- Segurança básica com hash de senha (SHA-256)

---

## ✅ Funcionalidades

### Acesso
- [x] Cadastro de conta com nome, CPF, idade e senha
- [x] Validação de CPF pelo algoritmo oficial da Receita Federal
- [x] Verificação de CPF duplicado
- [x] Senha com mínimo de 8 caracteres (armazenada com hash SHA-256)
- [x] Login com CPF e senha
- [x] Bloqueio automático após 3 tentativas incorretas de senha

### Operações bancárias
- [x] Consulta de saldo com dados completos da conta
- [x] Depósito com validação de valor positivo
- [x] Saque com validação de saldo, limite por operação (R$ 500) e limite diário (3 saques)
- [x] Transferência entre contas com confirmação antes de executar
- [x] Extrato completo com data, hora, tipo e valor de cada operação

### Interface
- [x] Menu interativo que permanece em loop até o usuário sair
- [x] Mensagens de erro claras e descritivas
- [x] Formatação monetária no padrão brasileiro (R$ 1.500,00)

---

## 🚀 Como executar

### Pré-requisitos

- Python **3.10 ou superior** (necessário para o `match/case`)

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/banco-python.git

# 2. Entre na pasta do projeto
cd banco-python

# 3. Execute o sistema
python banco.py
```

> Não há dependências externas. O projeto usa apenas a biblioteca padrão do Python.

### Navegação no sistema

```
══════════════════════════════════════════════════
                  BANCO PYTHON
──────────────────────────────────────────────────
                 Menu Principal
══════════════════════════════════════════════════

  1  →  Criar conta
  2  →  Entrar na conta
  3  →  Sair
```

Após o login:

```
══════════════════════════════════════════════════
                  BANCO PYTHON
──────────────────────────────────────────────────
              Bem-vindo(a), João!
══════════════════════════════════════════════════

  1  →  Ver saldo
  2  →  Depositar
  3  →  Sacar
  4  →  Transferir
  5  →  Ver extrato
  6  →  Sair da conta
```

---

## 🏗️ Arquitetura

O projeto é organizado em **camadas lógicas** dentro de um único arquivo, separadas por seções comentadas:

```
┌─────────────────────────────────────────────┐
│         Interface / Menus (fluxo_*)         │  → entrada e saída com o usuário
├─────────────────────────────────────────────┤
│             Banco (orquestrador)            │  → cadastro, autenticação, busca
├─────────────────────────────────────────────┤
│         Cliente  ←  herda  ←  Pessoa        │  → entidades do domínio
│         ContaCorrente  ←  herda  ←  Conta   │
├─────────────────────────────────────────────┤
│    Deposito / Saque / Transferencia (ABC)   │  → polimorfismo de transações
├─────────────────────────────────────────────┤
│          Historico  +  Exceções             │  → auditoria e erros de domínio
├─────────────────────────────────────────────┤
│              Utilitários                    │  → validações, formatação, hash
└─────────────────────────────────────────────┘
```

### Diagrama de classes simplificado

```
Pessoa
└── Cliente
      ├── _senha_hash (SHA-256)
      ├── _contas: List[Conta]
      └── verificar_senha()

Conta
└── ContaCorrente
      ├── _limite_saque
      ├── _max_saques_diarios
      └── sacar() ← override com regras extras

Transacao (ABC)
├── Deposito
├── Saque
├── TransferenciaEnviada
└── TransferenciaRecebida

Banco
├── _clientes: dict[cpf → Cliente]
├── _contas: dict[numero → Conta]
├── cadastrar_cliente()
├── autenticar_cliente()
└── buscar_conta()
```

---

## 🧱 Conceitos de POO aplicados

### Encapsulamento
Todos os atributos usam `_prefixo` (convenção de privado) e são expostos apenas via `@property`. O saldo nunca é alterado diretamente de fora — somente através de métodos como `depositar()` e `sacar()`. A senha nunca é armazenada em texto puro.

```python
@property
def saldo(self) -> float:
    return self._saldo  # leitura permitida

# self._saldo = x  ← isso seria feito de fora? Não. Só via depositar()/sacar()
```

### Herança
`Cliente` herda de `Pessoa`, reusando nome, CPF e idade. `ContaCorrente` herda de `Conta`, reusando toda a infraestrutura de saldo e histórico.

```python
class Cliente(Pessoa):       # herda nome, cpf, idade
class ContaCorrente(Conta):  # herda saldo, historico, depositar()
```

### Polimorfismo
`ContaCorrente.sacar()` faz *override* do método da classe base, adicionando validações de limite sem duplicar código. As 4 subclasses de `Transacao` implementam `tipo` e `simbolo` de formas diferentes — o `Historico` as trata de forma uniforme.

```python
# Conta.sacar()          → valida valor e saldo
# ContaCorrente.sacar()  → valida também limite e saques diários
```

### Abstração (ABC)
`Transacao` é uma classe abstrata que define o contrato que todas as operações devem seguir. Nenhuma instância direta é criada.

```python
class Transacao(ABC):
    @property
    @abstractmethod
    def tipo(self) -> str: ...  # obrigatório nas subclasses

    @property
    @abstractmethod
    def simbolo(self) -> str: ... # obrigatório nas subclasses
```

### Exceções customizadas
O projeto define 9 exceções próprias que comunicam erros de domínio com precisão, sem depender de mensagens genéricas.

```python
ErroSaldoInsuficiente
ErroLimiteSaque
ErroSaquesDiarios
ErroCPFInvalido
ErroCPFDuplicado
ErroSenhaInvalida
ErroAutenticacao
ErroValorInvalido
ErroConta
```

---

## 📁 Estrutura do projeto

```
banco-python/
├── banco.py      # sistema completo (1.064 linhas)
├── testes.py     # suite de testes automatizados (41 testes)
├── .gitignore
└── README.md
```

---

## 🧪 Executar os testes

```bash
python testes.py
```

Saída esperada:

```
══════════════════════════════════════════════════
          BANCO PYTHON — SUITE DE TESTES
══════════════════════════════════════════════════

📦 Utilitários e Validações
  ✅ PASSOU — CPF válido aceito
  ✅ PASSOU — CPF inválido rejeitado
  ...

📝 Cadastro de Clientes
  ✅ PASSOU — Cadastro com dados válidos
  ✅ PASSOU — CPF duplicado lança ErroCPFDuplicado
  ...

══════════════════════════════════════════════════
  RESULTADO FINAL: 41/41 testes passaram
  🎉 Todos os testes passaram!
══════════════════════════════════════════════════
```

Os testes cobrem:
- Utilitários (validação de CPF, hash, formatação)
- Cadastro (dados válidos, CPF duplicado, senha curta, menor de idade)
- Autenticação (login correto, CPF inexistente, senha errada, bloqueio)
- Operações (depósito, saque, limites, saques diários)
- Transferências (débito/crédito, histórico nos dois lados, mesma conta)
- Histórico (contagem de saques, tipos de transação)

---

## 🚀 Melhorias futuras

- [ ] **Persistência** — salvar dados com SQLite usando o módulo `sqlite3`
- [ ] **Conta Poupança** — nova subclasse com rendimento mensal (mais polimorfismo)
- [ ] **Testes com pytest** — migrar para fixtures e relatório de cobertura com `pytest-cov`
- [ ] **API REST** — expor as operações via FastAPI
- [ ] **Logs estruturados** — usar o módulo `logging` para auditoria em arquivo
- [ ] **Interface web** — frontend React consumindo a API

---

## 🛠️ Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.10+ | Linguagem principal |
| `abc` | Classes abstratas (`Transacao`) |
| `hashlib` | Hash SHA-256 para senhas |
| `datetime` | Registro de data/hora nas transações |
| `re` | Validação e limpeza de CPF |
| `random` | Geração de números de conta |

---

## ⚠️ Aviso

Este projeto foi gerado com auxílio de IA como exercício de aprendizado.
O código serve como referência de boas práticas, mas não representa
minha produção autoral em Python.
