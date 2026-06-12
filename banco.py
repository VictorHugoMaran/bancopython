"""
╔══════════════════════════════════════════════════════════╗
║              BANCO PYTHON - SISTEMA BANCÁRIO             ║
║         Projeto de Portfólio - POO com Python            ║
╚══════════════════════════════════════════════════════════╝

Arquitetura: Orientada a Objetos com camadas de modelo,
serviço e interface. Simula operações reais de um banco.

Autor: Projeto educacional para portfólio
"""

import hashlib
import os
import random
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional


# ─────────────────────────────────────────────
#  MÓDULO DE UTILITÁRIOS
# ─────────────────────────────────────────────

def limpar_tela() -> None:
    """Limpa o terminal para melhorar a experiência do usuário."""
    os.system("cls" if os.name == "nt" else "clear")


def formatar_moeda(valor: float) -> str:
    """Formata um valor float para o padrão monetário brasileiro."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_data(dt: datetime) -> str:
    """Formata um objeto datetime para o padrão brasileiro."""
    return dt.strftime("%d/%m/%Y às %H:%M:%S")


def gerar_numero_conta() -> str:
    """Gera um número de conta aleatório no formato XXXXX-X."""
    numero = random.randint(10000, 99999)
    digito = random.randint(0, 9)
    return f"{numero}-{digito}"


def validar_cpf(cpf: str) -> bool:
    """
    Valida um CPF usando o algoritmo oficial da Receita Federal.
    Remove pontuação antes de validar.
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r"\D", "", cpf)

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # Validação do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    primeiro_digito = (soma * 10 % 11) % 10
    if primeiro_digito != int(cpf[9]):
        return False

    # Validação do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    segundo_digito = (soma * 10 % 11) % 10
    return segundo_digito == int(cpf[10])


def hash_senha(senha: str) -> str:
    """Gera o hash SHA-256 de uma senha para armazenamento seguro."""
    return hashlib.sha256(senha.encode()).hexdigest()


def imprimir_separador(char: str = "─", largura: int = 50) -> None:
    """Imprime uma linha separadora formatada."""
    print(char * largura)


def imprimir_cabecalho(titulo: str) -> None:
    """Imprime um cabeçalho formatado com título centralizado."""
    print()
    imprimir_separador("═")
    print(f"{'BANCO PYTHON':^50}")
    imprimir_separador("─")
    print(f"{titulo:^50}")
    imprimir_separador("═")
    print()


# ─────────────────────────────────────────────
#  MÓDULO DE EXCEÇÕES CUSTOMIZADAS
# ─────────────────────────────────────────────

class ErroSaldoInsuficiente(Exception):
    """Levantada quando o saldo é insuficiente para a operação."""
    pass


class ErroLimiteSaque(Exception):
    """Levantada quando o valor excede o limite permitido por saque."""
    pass


class ErroSaquesDiarios(Exception):
    """Levantada quando o limite de saques diários é atingido."""
    pass


class ErroCPFInvalido(Exception):
    """Levantada quando o CPF informado não é válido."""
    pass


class ErroCPFDuplicado(Exception):
    """Levantada quando o CPF já está cadastrado no sistema."""
    pass


class ErroContaNaoEncontrada(Exception):
    """Levantada quando a conta de destino não é encontrada."""
    pass


class ErroSenhaInvalida(Exception):
    """Levantada quando a senha não atende aos requisitos mínimos."""
    pass


class ErroValorInvalido(Exception):
    """Levantada quando o valor informado é inválido (negativo ou zero)."""
    pass


class ErroAutenticacao(Exception):
    """Levantada quando as credenciais de login estão incorretas."""
    pass


class ErroConta(Exception):
    """Exceção genérica para erros relacionados à conta."""
    pass


# ─────────────────────────────────────────────
#  MÓDULO DE TRANSAÇÕES (Polimorfismo via ABC)
# ─────────────────────────────────────────────

class Transacao(ABC):
    """
    Classe abstrata base para todas as transações bancárias.
    Implementa o padrão Template Method: define a estrutura de
    uma transação, mas delega a implementação do tipo à subclasse.
    """

    def __init__(self, valor: float, descricao: str = "") -> None:
        self._valor: float = valor
        self._descricao: str = descricao
        self._data_hora: datetime = datetime.now()

    @property
    def valor(self) -> float:
        return self._valor

    @property
    def descricao(self) -> str:
        return self._descricao

    @property
    def data_hora(self) -> datetime:
        return self._data_hora

    @property
    @abstractmethod
    def tipo(self) -> str:
        """Retorna o tipo da transação (ex: 'Depósito', 'Saque')."""
        pass

    @property
    @abstractmethod
    def simbolo(self) -> str:
        """Retorna o símbolo visual (+/-) para exibição no extrato."""
        pass

    def __str__(self) -> str:
        return (
            f"[{formatar_data(self._data_hora)}] "
            f"{self.tipo:<20} "
            f"{self.simbolo} {formatar_moeda(self._valor):<15} "
            f"| {self._descricao}"
        )


class Deposito(Transacao):
    """Representa uma operação de depósito."""

    @property
    def tipo(self) -> str:
        return "Depósito"

    @property
    def simbolo(self) -> str:
        return "+"


class Saque(Transacao):
    """Representa uma operação de saque."""

    @property
    def tipo(self) -> str:
        return "Saque"

    @property
    def simbolo(self) -> str:
        return "-"


class TransferenciaEnviada(Transacao):
    """Representa uma transferência enviada para outra conta."""

    def __init__(self, valor: float, conta_destino: str, descricao: str = "") -> None:
        super().__init__(valor, descricao)
        self._conta_destino: str = conta_destino

    @property
    def tipo(self) -> str:
        return "Transferência Enviada"

    @property
    def simbolo(self) -> str:
        return "-"

    @property
    def conta_destino(self) -> str:
        return self._conta_destino

    def __str__(self) -> str:
        return (
            f"[{formatar_data(self._data_hora)}] "
            f"{self.tipo:<20} "
            f"{self.simbolo} {formatar_moeda(self._valor):<15} "
            f"| Para conta {self._conta_destino}"
        )


class TransferenciaRecebida(Transacao):
    """Representa uma transferência recebida de outra conta."""

    def __init__(self, valor: float, conta_origem: str, descricao: str = "") -> None:
        super().__init__(valor, descricao)
        self._conta_origem: str = conta_origem

    @property
    def tipo(self) -> str:
        return "Transferência Recebida"

    @property
    def simbolo(self) -> str:
        return "+"

    @property
    def conta_origem(self) -> str:
        return self._conta_origem

    def __str__(self) -> str:
        return (
            f"[{formatar_data(self._data_hora)}] "
            f"{self.tipo:<20} "
            f"{self.simbolo} {formatar_moeda(self._valor):<15} "
            f"| De conta {self._conta_origem}"
        )


# ─────────────────────────────────────────────
#  MÓDULO DE HISTÓRICO
# ─────────────────────────────────────────────

class Historico:
    """
    Gerencia o histórico de transações de uma conta.
    Responsabilidade única: armazenar e recuperar transações.
    """

    def __init__(self) -> None:
        self._transacoes: List[Transacao] = []

    def adicionar(self, transacao: Transacao) -> None:
        """Adiciona uma transação ao histórico."""
        self._transacoes.append(transacao)

    @property
    def transacoes(self) -> List[Transacao]:
        """Retorna uma cópia da lista de transações (imutabilidade)."""
        return list(self._transacoes)

    def total_saques_hoje(self) -> int:
        """Conta quantos saques foram realizados no dia atual."""
        hoje = datetime.now().date()
        return sum(
            1 for t in self._transacoes
            if isinstance(t, Saque) and t.data_hora.date() == hoje
        )

    def imprimir_extrato(self) -> None:
        """Exibe o extrato formatado no terminal."""
        if not self._transacoes:
            print("\n  Nenhuma transação registrada ainda.")
            return

        print()
        imprimir_separador("─")
        print(f"  {'DATA/HORA':<26} {'TIPO':<20} {'VALOR':<18} DESCRIÇÃO")
        imprimir_separador("─")

        for transacao in self._transacoes:
            print(f"  {transacao}")

        imprimir_separador("─")


# ─────────────────────────────────────────────
#  MÓDULO DE CONTAS (Herança)
# ─────────────────────────────────────────────

class Conta:
    """
    Classe base para todos os tipos de conta bancária.
    Encapsula saldo, número e agência, além do histórico.
    """

    AGENCIA_PADRAO: str = "0001"

    def __init__(self, numero: str, titular: "Cliente") -> None:
        self._numero: str = numero
        self._agencia: str = Conta.AGENCIA_PADRAO
        self._saldo: float = 0.0
        self._titular: "Cliente" = titular
        self._historico: Historico = Historico()
        self._ativa: bool = True

    # ── Propriedades (encapsulamento via @property) ──

    @property
    def numero(self) -> str:
        return self._numero

    @property
    def agencia(self) -> str:
        return self._agencia

    @property
    def saldo(self) -> float:
        return self._saldo

    @property
    def titular(self) -> "Cliente":
        return self._titular

    @property
    def historico(self) -> Historico:
        return self._historico

    @property
    def ativa(self) -> bool:
        return self._ativa

    # ── Operações bancárias base ──

    def depositar(self, valor: float) -> None:
        """
        Deposita um valor na conta.
        Lança ErroValorInvalido se o valor for inválido.
        """
        if valor <= 0:
            raise ErroValorInvalido("O valor do depósito deve ser positivo.")

        self._saldo += valor
        transacao = Deposito(valor, "Depósito em conta")
        self._historico.adicionar(transacao)

    def sacar(self, valor: float) -> None:
        """
        Realiza um saque. Método base, sem limite — as subclasses
        adicionam suas próprias regras via override (polimorfismo).
        """
        if valor <= 0:
            raise ErroValorInvalido("O valor do saque deve ser positivo.")
        if valor > self._saldo:
            raise ErroSaldoInsuficiente(
                f"Saldo insuficiente. Saldo atual: {formatar_moeda(self._saldo)}"
            )

        self._saldo -= valor
        transacao = Saque(valor, "Saque em conta")
        self._historico.adicionar(transacao)

    def transferir(self, valor: float, conta_destino: "Conta") -> None:
        """
        Transfere valor para outra conta.
        Registra a transação no histórico de ambas as contas.
        """
        if valor <= 0:
            raise ErroValorInvalido("O valor da transferência deve ser positivo.")
        if conta_destino.numero == self._numero:
            raise ErroConta("Não é possível transferir para a própria conta.")

        # Realiza o saque (pode lançar exceções próprias da subclasse)
        self.sacar(valor)

        # Reverte o saque do histórico (registramos como TransferenciaEnviada)
        self._historico._transacoes.pop()

        # Credita na conta de destino
        conta_destino._saldo += valor

        # Registra nas duas contas
        self._historico.adicionar(
            TransferenciaEnviada(valor, conta_destino.numero)
        )
        conta_destino._historico.adicionar(
            TransferenciaRecebida(valor, self._numero)
        )

    def __str__(self) -> str:
        return (
            f"Conta: {self._numero} | "
            f"Agência: {self._agencia} | "
            f"Titular: {self._titular.nome} | "
            f"Saldo: {formatar_moeda(self._saldo)}"
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} numero={self._numero!r}>"


class ContaCorrente(Conta):
    """
    Especialização de Conta com regras específicas:
    - Limite máximo por saque
    - Limite de saques diários
    Demonstra herança e polimorfismo (override de sacar).
    """

    LIMITE_SAQUE_PADRAO: float = 500.0
    MAX_SAQUES_DIARIOS: int = 3

    def __init__(
        self,
        numero: str,
        titular: "Cliente",
        limite_saque: float = LIMITE_SAQUE_PADRAO,
        max_saques_diarios: int = MAX_SAQUES_DIARIOS,
    ) -> None:
        super().__init__(numero, titular)
        self._limite_saque: float = limite_saque
        self._max_saques_diarios: int = max_saques_diarios

    @property
    def limite_saque(self) -> float:
        return self._limite_saque

    @property
    def max_saques_diarios(self) -> int:
        return self._max_saques_diarios

    def sacar(self, valor: float) -> None:
        """
        Override do método sacar com validações adicionais
        específicas da Conta Corrente (polimorfismo).
        """
        if valor <= 0:
            raise ErroValorInvalido("O valor do saque deve ser positivo.")

        if valor > self._limite_saque:
            raise ErroLimiteSaque(
                f"Valor excede o limite por saque de {formatar_moeda(self._limite_saque)}."
            )

        saques_hoje = self._historico.total_saques_hoje()
        if saques_hoje >= self._max_saques_diarios:
            raise ErroSaquesDiarios(
                f"Limite de {self._max_saques_diarios} saques diários atingido."
            )

        if valor > self._saldo:
            raise ErroSaldoInsuficiente(
                f"Saldo insuficiente. Saldo atual: {formatar_moeda(self._saldo)}"
            )

        self._saldo -= valor
        self._historico.adicionar(Saque(valor, "Saque em conta corrente"))

    def __str__(self) -> str:
        return (
            f"[Conta Corrente] "
            f"Nº {self._numero} | "
            f"Ag. {self._agencia} | "
            f"Titular: {self._titular.nome} | "
            f"Saldo: {formatar_moeda(self._saldo)}"
        )


# ─────────────────────────────────────────────
#  MÓDULO DE PESSOAS / CLIENTES (Herança)
# ─────────────────────────────────────────────

class Pessoa:
    """
    Classe base representando uma pessoa física.
    Encapsula dados pessoais comuns.
    """

    def __init__(self, nome: str, cpf: str, idade: int) -> None:
        self._nome: str = nome
        self._cpf: str = re.sub(r"\D", "", cpf)  # Armazena apenas dígitos
        self._idade: int = idade

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def cpf(self) -> str:
        return self._cpf

    @property
    def cpf_formatado(self) -> str:
        """Retorna o CPF no formato XXX.XXX.XXX-XX."""
        c = self._cpf
        return f"{c[:3]}.{c[3:6]}.{c[6:9]}-{c[9:]}"

    @property
    def idade(self) -> int:
        return self._idade

    def __str__(self) -> str:
        return f"{self._nome} (CPF: {self.cpf_formatado})"

    def __repr__(self) -> str:
        return f"<Pessoa nome={self._nome!r} cpf={self._cpf!r}>"


class Cliente(Pessoa):
    """
    Especialização de Pessoa que representa um cliente bancário.
    Possui autenticação, lista de contas e conta ativa.
    Herda os dados pessoais de Pessoa.
    """

    MAX_TENTATIVAS_LOGIN: int = 3

    def __init__(self, nome: str, cpf: str, idade: int, senha: str) -> None:
        super().__init__(nome, cpf, idade)
        self._senha_hash: str = hash_senha(senha)
        self._contas: List[Conta] = []
        self._conta_ativa: Optional[Conta] = None
        self._tentativas_login: int = 0
        self._bloqueado: bool = False
        self._data_cadastro: datetime = datetime.now()

    @property
    def contas(self) -> List[Conta]:
        return list(self._contas)

    @property
    def conta_ativa(self) -> Optional[Conta]:
        return self._conta_ativa

    @property
    def bloqueado(self) -> bool:
        return self._bloqueado

    @property
    def data_cadastro(self) -> datetime:
        return self._data_cadastro

    def adicionar_conta(self, conta: Conta) -> None:
        """Vincula uma conta ao cliente."""
        self._contas.append(conta)
        if self._conta_ativa is None:
            self._conta_ativa = conta

    def verificar_senha(self, senha: str) -> bool:
        """
        Verifica se a senha informada está correta.
        Controla tentativas e bloqueia o cliente após exceder o limite.
        """
        if self._bloqueado:
            raise ErroAutenticacao(
                "Conta bloqueada por excesso de tentativas. "
                "Entre em contato com o suporte."
            )

        if hash_senha(senha) == self._senha_hash:
            self._tentativas_login = 0  # Reset ao logar com sucesso
            return True

        self._tentativas_login += 1
        restantes = self.MAX_TENTATIVAS_LOGIN - self._tentativas_login

        if self._tentativas_login >= self.MAX_TENTATIVAS_LOGIN:
            self._bloqueado = True
            raise ErroAutenticacao(
                "Conta bloqueada por excesso de tentativas. "
                "Entre em contato com o suporte."
            )

        raise ErroAutenticacao(
            f"Senha incorreta. Você tem {restantes} tentativa(s) restante(s)."
        )

    def __str__(self) -> str:
        return (
            f"Cliente: {self._nome} | "
            f"CPF: {self.cpf_formatado} | "
            f"Contas: {len(self._contas)}"
        )

    def __repr__(self) -> str:
        return f"<Cliente nome={self._nome!r} cpf={self._cpf!r}>"


# ─────────────────────────────────────────────
#  MÓDULO DO BANCO (Orquestrador)
# ─────────────────────────────────────────────

class Banco:
    """
    Classe principal que orquestra todo o sistema bancário.
    Responsável por:
    - Cadastro de clientes
    - Autenticação
    - Criação de contas
    - Busca de contas para transferência
    """

    def __init__(self, nome: str) -> None:
        self._nome: str = nome
        self._clientes: dict[str, Cliente] = {}  # cpf -> Cliente
        self._contas: dict[str, Conta] = {}      # numero -> Conta
        self._numeros_gerados: set[str] = set()

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def total_clientes(self) -> int:
        return len(self._clientes)

    @property
    def total_contas(self) -> int:
        return len(self._contas)

    def _gerar_numero_unico(self) -> str:
        """Gera um número de conta único (sem colisão)."""
        while True:
            numero = gerar_numero_conta()
            if numero not in self._numeros_gerados:
                self._numeros_gerados.add(numero)
                return numero

    def cadastrar_cliente(
        self, nome: str, cpf: str, idade: int, senha: str
    ) -> Cliente:
        """
        Cadastra um novo cliente e cria automaticamente uma conta corrente.
        Aplica todas as validações de negócio.
        """
        cpf_limpo = re.sub(r"\D", "", cpf)

        # Validações
        if not validar_cpf(cpf_limpo):
            raise ErroCPFInvalido("O CPF informado não é válido.")

        if cpf_limpo in self._clientes:
            raise ErroCPFDuplicado("Este CPF já está cadastrado no sistema.")

        if len(senha) < 8:
            raise ErroSenhaInvalida("A senha deve ter no mínimo 8 caracteres.")

        if not nome.strip():
            raise ValueError("O nome não pode estar em branco.")

        if idade < 18:
            raise ValueError("É necessário ser maior de idade para abrir uma conta.")

        # Criação do cliente
        cliente = Cliente(nome.strip().title(), cpf_limpo, idade, senha)

        # Criação automática da conta corrente
        numero = self._gerar_numero_unico()
        conta = ContaCorrente(numero, cliente)

        cliente.adicionar_conta(conta)
        self._clientes[cpf_limpo] = cliente
        self._contas[numero] = conta

        return cliente

    def autenticar_cliente(self, cpf: str, senha: str) -> Cliente:
        """
        Autentica um cliente pelo CPF e senha.
        Lança ErroAutenticacao em caso de falha.
        """
        cpf_limpo = re.sub(r"\D", "", cpf)
        cliente = self._clientes.get(cpf_limpo)

        if not cliente:
            raise ErroAutenticacao("CPF não encontrado no sistema.")

        # verificar_senha já lança exceção com mensagem adequada
        cliente.verificar_senha(senha)
        return cliente

    def buscar_conta(self, numero: str) -> Optional[Conta]:
        """Busca uma conta pelo número. Retorna None se não encontrar."""
        return self._contas.get(numero)

    def __str__(self) -> str:
        return (
            f"Banco: {self._nome} | "
            f"Clientes: {self.total_clientes} | "
            f"Contas: {self.total_contas}"
        )

    def __repr__(self) -> str:
        return f"<Banco nome={self._nome!r}>"


# ─────────────────────────────────────────────
#  CAMADA DE INTERFACE / MENUS
# ─────────────────────────────────────────────

def menu_principal() -> str:
    """Exibe o menu principal e retorna a opção escolhida."""
    imprimir_cabecalho("Menu Principal")
    print("  1  →  Criar conta")
    print("  2  →  Entrar na conta")
    print("  3  →  Sair")
    print()
    imprimir_separador()
    return input("  Escolha uma opção: ").strip()


def menu_logado(nome_cliente: str) -> str:
    """Exibe o menu do cliente autenticado e retorna a opção."""
    imprimir_cabecalho(f"Bem-vindo(a), {nome_cliente.split()[0]}!")
    print("  1  →  Ver saldo")
    print("  2  →  Depositar")
    print("  3  →  Sacar")
    print("  4  →  Transferir")
    print("  5  →  Ver extrato")
    print("  6  →  Sair da conta")
    print()
    imprimir_separador()
    return input("  Escolha uma opção: ").strip()


def ler_valor(mensagem: str) -> float:
    """
    Lê e converte um valor monetário do terminal.
    Lança ValueError se o formato for inválido.
    """
    entrada = input(mensagem).strip().replace(",", ".")
    try:
        valor = float(entrada)
        return valor
    except ValueError:
        raise ValueError("Valor inválido. Use formato numérico (ex: 150.00).")


# ─────────────────────────────────────────────
#  FLUXOS DE CADASTRO E LOGIN
# ─────────────────────────────────────────────

def fluxo_criar_conta(banco: Banco) -> None:
    """Coleta os dados e cadastra um novo cliente no banco."""
    limpar_tela()
    imprimir_cabecalho("Criar Nova Conta")

    print("  Preencha os dados abaixo para criar sua conta.\n")

    try:
        nome = input("  Nome completo: ").strip()
        if not nome:
            print("\n  ❌  O nome não pode estar em branco.")
            input("\n  Pressione Enter para voltar...")
            return

        cpf = input("  CPF (somente números): ").strip()

        try:
            idade = int(input("  Idade: ").strip())
        except ValueError:
            print("\n  ❌  Idade inválida. Informe um número inteiro.")
            input("\n  Pressione Enter para voltar...")
            return

        print()
        print("  A senha deve ter no mínimo 8 caracteres.")
        senha = input("  Crie uma senha: ").strip()
        confirmacao = input("  Confirme a senha: ").strip()

        if senha != confirmacao:
            print("\n  ❌  As senhas não coincidem.")
            input("\n  Pressione Enter para voltar...")
            return

        # Tenta cadastrar — pode lançar diversas exceções
        cliente = banco.cadastrar_cliente(nome, cpf, idade, senha)
        conta = cliente.conta_ativa

        limpar_tela()
        imprimir_cabecalho("Conta Criada com Sucesso!")
        print(f"  ✅  Bem-vindo(a), {cliente.nome}!")
        print()
        print(f"  Nome    : {cliente.nome}")
        print(f"  CPF     : {cliente.cpf_formatado}")
        print(f"  Conta   : {conta.numero}")
        print(f"  Agência : {conta.agencia}")
        print(f"  Saldo   : {formatar_moeda(conta.saldo)}")
        print(f"  Cadastro: {formatar_data(cliente.data_cadastro)}")
        print()
        imprimir_separador()

    except (ErroCPFInvalido, ErroCPFDuplicado, ErroSenhaInvalida, ValueError) as e:
        print(f"\n  ❌  Erro ao criar conta: {e}")

    input("\n  Pressione Enter para voltar ao menu...")


def fluxo_login(banco: Banco) -> Optional[Cliente]:
    """Autentica o cliente e retorna o objeto Cliente ou None."""
    limpar_tela()
    imprimir_cabecalho("Entrar na Conta")

    cpf = input("  CPF: ").strip()
    senha = input("  Senha: ").strip()

    try:
        cliente = banco.autenticar_cliente(cpf, senha)
        print(f"\n  ✅  Login realizado com sucesso!")
        input("  Pressione Enter para continuar...")
        return cliente
    except ErroAutenticacao as e:
        print(f"\n  ❌  {e}")
        input("\n  Pressione Enter para voltar...")
        return None


# ─────────────────────────────────────────────
#  FLUXOS DAS OPERAÇÕES BANCÁRIAS
# ─────────────────────────────────────────────

def fluxo_ver_saldo(cliente: Cliente) -> None:
    """Exibe os dados da conta e saldo atual."""
    limpar_tela()
    conta = cliente.conta_ativa
    imprimir_cabecalho("Consulta de Saldo")
    print(f"  Titular  : {cliente.nome}")
    print(f"  CPF      : {cliente.cpf_formatado}")
    print(f"  Conta    : {conta.numero}")
    print(f"  Agência  : {conta.agencia}")
    print(f"  Tipo     : Conta Corrente")
    print()
    imprimir_separador()
    print(f"  {'SALDO DISPONÍVEL':^46}")
    imprimir_separador()
    print(f"  {formatar_moeda(conta.saldo):^46}")
    imprimir_separador()
    input("\n  Pressione Enter para voltar...")


def fluxo_depositar(cliente: Cliente) -> None:
    """Fluxo completo para realizar um depósito."""
    limpar_tela()
    conta = cliente.conta_ativa
    imprimir_cabecalho("Depositar")
    print(f"  Conta: {conta.numero} | Saldo atual: {formatar_moeda(conta.saldo)}\n")

    try:
        valor = ler_valor("  Valor do depósito (R$): ")
        conta.depositar(valor)
        print(f"\n  ✅  Depósito de {formatar_moeda(valor)} realizado com sucesso!")
        print(f"  Novo saldo: {formatar_moeda(conta.saldo)}")
    except (ErroValorInvalido, ValueError) as e:
        print(f"\n  ❌  {e}")

    input("\n  Pressione Enter para voltar...")


def fluxo_sacar(cliente: Cliente) -> None:
    """Fluxo completo para realizar um saque."""
    limpar_tela()
    conta = cliente.conta_ativa
    imprimir_cabecalho("Sacar")

    # Exibe informações importantes antes de sacar
    saques_hoje = conta.historico.total_saques_hoje()
    print(f"  Conta      : {conta.numero}")
    print(f"  Saldo atual: {formatar_moeda(conta.saldo)}")
    print(f"  Limite/saque: {formatar_moeda(conta.limite_saque)}")
    print(f"  Saques hoje : {saques_hoje}/{conta.max_saques_diarios}")
    print()

    try:
        valor = ler_valor("  Valor do saque (R$): ")
        conta.sacar(valor)
        print(f"\n  ✅  Saque de {formatar_moeda(valor)} realizado com sucesso!")
        print(f"  Novo saldo: {formatar_moeda(conta.saldo)}")
    except (ErroSaldoInsuficiente, ErroLimiteSaque, ErroSaquesDiarios, ErroValorInvalido, ValueError) as e:
        print(f"\n  ❌  {e}")

    input("\n  Pressione Enter para voltar...")


def fluxo_transferir(cliente: Cliente, banco: Banco) -> None:
    """Fluxo completo para realizar uma transferência entre contas."""
    limpar_tela()
    conta_origem = cliente.conta_ativa
    imprimir_cabecalho("Transferência")
    print(f"  Conta de origem : {conta_origem.numero}")
    print(f"  Saldo disponível: {formatar_moeda(conta_origem.saldo)}\n")

    numero_destino = input("  Número da conta de destino: ").strip()

    if not numero_destino:
        print("\n  ❌  Número da conta não pode estar em branco.")
        input("\n  Pressione Enter para voltar...")
        return

    conta_destino = banco.buscar_conta(numero_destino)
    if not conta_destino:
        print(f"\n  ❌  Conta {numero_destino} não encontrada.")
        input("\n  Pressione Enter para voltar...")
        return

    if conta_destino.numero == conta_origem.numero:
        print("\n  ❌  Não é possível transferir para a própria conta.")
        input("\n  Pressione Enter para voltar...")
        return

    print(f"\n  Destino confirmado: {conta_destino.titular.nome}")

    try:
        valor = ler_valor("  Valor da transferência (R$): ")

        # Confirmação antes de executar
        print(f"\n  Você está prestes a transferir {formatar_moeda(valor)}")
        print(f"  para {conta_destino.titular.nome} (conta {conta_destino.numero}).")
        confirmar = input("\n  Confirmar transferência? (s/n): ").strip().lower()

        if confirmar != "s":
            print("\n  Transferência cancelada.")
            input("\n  Pressione Enter para voltar...")
            return

        conta_origem.transferir(valor, conta_destino)
        print(f"\n  ✅  Transferência de {formatar_moeda(valor)} realizada com sucesso!")
        print(f"  Novo saldo: {formatar_moeda(conta_origem.saldo)}")

    except (ErroSaldoInsuficiente, ErroLimiteSaque, ErroSaquesDiarios, ErroValorInvalido, ErroConta, ValueError) as e:
        print(f"\n  ❌  {e}")

    input("\n  Pressione Enter para voltar...")


def fluxo_ver_extrato(cliente: Cliente) -> None:
    """Exibe o extrato completo da conta do cliente."""
    limpar_tela()
    conta = cliente.conta_ativa
    imprimir_cabecalho("Extrato Bancário")
    print(f"  Conta: {conta.numero} | Agência: {conta.agencia}")
    print(f"  Titular: {cliente.nome}")
    print()

    conta.historico.imprimir_extrato()

    print(f"\n  Saldo atual: {formatar_moeda(conta.saldo)}")
    input("\n  Pressione Enter para voltar...")


# ─────────────────────────────────────────────
#  LOOP PRINCIPAL DO SISTEMA
# ─────────────────────────────────────────────

def loop_cliente_logado(cliente: Cliente, banco: Banco) -> None:
    """
    Mantém o cliente navegando nas opções bancárias
    até que ele escolha sair da conta.
    """
    while True:
        limpar_tela()
        opcao = menu_logado(cliente.nome)

        match opcao:
            case "1":
                limpar_tela()
                fluxo_ver_saldo(cliente)
            case "2":
                limpar_tela()
                fluxo_depositar(cliente)
            case "3":
                limpar_tela()
                fluxo_sacar(cliente)
            case "4":
                limpar_tela()
                fluxo_transferir(cliente, banco)
            case "5":
                limpar_tela()
                fluxo_ver_extrato(cliente)
            case "6":
                print(f"\n  Até logo, {cliente.nome.split()[0]}! 👋")
                input("  Pressione Enter para voltar ao menu principal...")
                break
            case _:
                print("\n  ❌  Opção inválida. Tente novamente.")
                input("  Pressione Enter para continuar...")


def iniciar_sistema() -> None:
    """
    Ponto de entrada da aplicação.
    Inicializa o banco e mantém o loop do menu principal.
    """
    banco = Banco("Banco Python")

    while True:
        limpar_tela()
        opcao = menu_principal()

        match opcao:
            case "1":
                limpar_tela()
                fluxo_criar_conta(banco)
            case "2":
                limpar_tela()
                cliente = fluxo_login(banco)
                if cliente:
                    loop_cliente_logado(cliente, banco)
            case "3":
                limpar_tela()
                print()
                imprimir_separador("═")
                print(f"{'BANCO PYTHON':^50}")
                imprimir_separador("─")
                print(f"{'Obrigado por usar nossos serviços!':^50}")
                print(f"{'Até logo! 👋':^50}")
                imprimir_separador("═")
                print()
                break
            case _:
                print("\n  ❌  Opção inválida. Tente novamente.")
                input("  Pressione Enter para continuar...")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    iniciar_sistema()
