"""
Testes automatizados para o Sistema Bancário Python.
Valida as principais regras de negócio e casos de borda.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from banco import (
    Banco, Cliente, ContaCorrente, Historico,
    Deposito, Saque, TransferenciaEnviada, TransferenciaRecebida,
    ErroSaldoInsuficiente, ErroLimiteSaque, ErroSaquesDiarios,
    ErroCPFInvalido, ErroCPFDuplicado, ErroSenhaInvalida,
    ErroAutenticacao, ErroValorInvalido, ErroConta,
    validar_cpf, hash_senha, formatar_moeda
)

PASSOU = "✅ PASSOU"
FALHOU = "❌ FALHOU"
resultados = []

# CPFs válidos gerados para os testes
CPF_JOAO      = "50043860648"
CPF_MARIA     = "05800472459"
CPF_TEEN      = "06585177754"
CPF_CARLOS    = "83317247630"
CPF_TESTER    = "97735154941"
CPF_REMETENTE = "90400555301"
CPF_DESTINAT  = "23066420876"
CPF_HIST      = "23601404770"


def testar(nome, condicao):
    status = PASSOU if condicao else FALHOU
    print(f"  {status} — {nome}")
    resultados.append((nome, condicao))


def esperar_excecao(func, excecao_esperada):
    try:
        func()
        return False
    except excecao_esperada:
        return True
    except Exception:
        return False


def testar_utilitarios():
    print("\n📦 Utilitários e Validações")
    print("─" * 45)
    testar("CPF válido aceito",          validar_cpf("529.982.247-25"))
    testar("CPF inválido rejeitado",     not validar_cpf("111.111.111-11"))
    testar("CPF curto rejeitado",        not validar_cpf("123"))
    testar("Hash senha retorna string",  isinstance(hash_senha("senha123"), str))
    testar("Hash senha é determinístico",hash_senha("abc") == hash_senha("abc"))
    testar("Hashes diferentes",          hash_senha("abc") != hash_senha("xyz"))
    testar("Formatar moeda funciona",    formatar_moeda(1500.50) == "R$ 1.500,50")


def testar_cadastro(banco):
    print("\n📝 Cadastro de Clientes")
    print("─" * 45)

    try:
        cliente = banco.cadastrar_cliente("João Silva", CPF_JOAO, 25, "senha123")
        testar("Cadastro com dados válidos",    cliente is not None)
        testar("Nome formatado com title()",    cliente.nome == "João Silva")
        testar("Conta criada automaticamente",  len(cliente.contas) == 1)
        testar("Conta ativa definida",          cliente.conta_ativa is not None)
        testar("Saldo inicial é zero",          cliente.conta_ativa.saldo == 0.0)
    except Exception as e:
        testar(f"Cadastro com dados válidos (erro: {e})", False)

    testar("CPF duplicado lança ErroCPFDuplicado",
        esperar_excecao(
            lambda: banco.cadastrar_cliente("Maria", CPF_JOAO, 30, "senha456"),
            ErroCPFDuplicado))

    testar("CPF inválido lança ErroCPFInvalido",
        esperar_excecao(
            lambda: banco.cadastrar_cliente("Pedro", "111.111.111-11", 22, "senha789"),
            ErroCPFInvalido))

    testar("Senha curta lança ErroSenhaInvalida",
        esperar_excecao(
            lambda: banco.cadastrar_cliente("Ana", CPF_MARIA, 20, "123"),
            ErroSenhaInvalida))

    testar("Menor de idade lança ValueError",
        esperar_excecao(
            lambda: banco.cadastrar_cliente("Teen", CPF_TEEN, 16, "senha123"),
            ValueError))


def testar_autenticacao(banco):
    print("\n🔐 Autenticação")
    print("─" * 45)

    try:
        banco.cadastrar_cliente("Carlos Auth", CPF_CARLOS, 35, "minhasenha")
    except ErroCPFDuplicado:
        pass

    try:
        cliente = banco.autenticar_cliente(CPF_CARLOS, "minhasenha")
        testar("Login com credenciais corretas", True)
        testar("Cliente retornado no login", cliente.nome == "Carlos Auth")
    except Exception as e:
        testar("Login com credenciais corretas", False)
        testar("Cliente retornado no login", False)

    testar("CPF inexistente lança ErroAutenticacao",
        esperar_excecao(
            lambda: banco.autenticar_cliente("00000000000", "qualquer"),
            ErroAutenticacao))

    testar("Senha errada lança ErroAutenticacao",
        esperar_excecao(
            lambda: banco.autenticar_cliente(CPF_CARLOS, "senhaerrada"),
            ErroAutenticacao))


def testar_operacoes_bancarias(banco):
    print("\n💰 Operações Bancárias")
    print("─" * 45)

    try:
        cliente = banco.cadastrar_cliente("Tester Ops", CPF_TESTER, 28, "testsenha")
    except ErroCPFDuplicado:
        cliente = banco.autenticar_cliente(CPF_TESTER, "testsenha")

    conta = cliente.conta_ativa

    conta.depositar(1000.0)
    testar("Depósito atualiza saldo",           conta.saldo == 1000.0)
    testar("Depósito no histórico",             len(conta.historico.transacoes) == 1)
    testar("Tipo Deposito no histórico",        isinstance(conta.historico.transacoes[0], Deposito))

    testar("Depósito zero lança ErroValorInvalido",
        esperar_excecao(lambda: conta.depositar(0), ErroValorInvalido))
    testar("Depósito negativo lança ErroValorInvalido",
        esperar_excecao(lambda: conta.depositar(-50), ErroValorInvalido))

    conta.sacar(200.0)
    testar("Saque atualiza saldo",              conta.saldo == 800.0)
    testar("Saque no histórico",                len(conta.historico.transacoes) == 2)

    testar("Saque acima do limite lança ErroLimiteSaque",
        esperar_excecao(lambda: conta.sacar(600.0), ErroLimiteSaque))
    # Para testar saldo insuficiente sem acionar o limite de saque,
    # criamos uma sub-conta com saldo menor que o limite por operação
    from banco import ContaCorrente as CC
    _cliente_tmp = type("_", (), {"nome": "Tmp"})()
    _cc = CC("00000-0", _cliente_tmp)
    _cc.depositar(100.0)
    testar("Saque acima do saldo lança ErroSaldoInsuficiente",
        esperar_excecao(lambda: _cc.sacar(200.0), ErroSaldoInsuficiente))
    testar("Saque negativo lança ErroValorInvalido",
        esperar_excecao(lambda: conta.sacar(-10), ErroValorInvalido))

    conta.sacar(100.0)   # 2º saque
    conta.sacar(100.0)   # 3º saque (limite)
    testar("4º saque no mesmo dia lança ErroSaquesDiarios",
        esperar_excecao(lambda: conta.sacar(50.0), ErroSaquesDiarios))


def testar_transferencias(banco):
    print("\n🔄 Transferências")
    print("─" * 45)

    try:
        origem  = banco.cadastrar_cliente("Remetente", CPF_REMETENTE, 30, "senhaorigem")
        destino = banco.cadastrar_cliente("Destinatário", CPF_DESTINAT, 32, "senhadestino")
    except ErroCPFDuplicado:
        origem  = banco.autenticar_cliente(CPF_REMETENTE, "senhaorigem")
        destino = banco.autenticar_cliente(CPF_DESTINAT, "senhadestino")

    co = origem.conta_ativa
    cd = destino.conta_ativa

    co.depositar(1000.0)
    saldo_destino_antes = cd.saldo

    co.transferir(300.0, cd)

    testar("Transferência debita da origem",     co.saldo == 700.0)
    testar("Transferência credita no destino",   cd.saldo == saldo_destino_antes + 300.0)

    hist_o = co.historico.transacoes
    hist_d = cd.historico.transacoes

    testar("TransferenciaEnviada no histórico de origem",
        any(isinstance(t, TransferenciaEnviada) for t in hist_o))
    testar("TransferenciaRecebida no histórico de destino",
        any(isinstance(t, TransferenciaRecebida) for t in hist_d))

    testar("Conta inexistente retorna None", banco.buscar_conta("99999-9") is None)

    testar("Transferência para mesma conta lança ErroConta",
        esperar_excecao(lambda: co.transferir(50.0, co), ErroConta))


def testar_historico(banco):
    print("\n📋 Histórico e Extrato")
    print("─" * 45)

    try:
        cliente = banco.cadastrar_cliente("Hist Cliente", CPF_HIST, 25, "historico1")
    except ErroCPFDuplicado:
        cliente = banco.autenticar_cliente(CPF_HIST, "historico1")

    conta = cliente.conta_ativa

    testar("Histórico inicia vazio", len(conta.historico.transacoes) == 0)

    conta.depositar(500.0)
    conta.depositar(300.0)
    conta.sacar(100.0)

    testar("Histórico registra 3 operações",     len(conta.historico.transacoes) == 3)
    testar("1 saque contado hoje",               conta.historico.total_saques_hoje() == 1)
    testar("__str__ da transação retorna string", isinstance(str(conta.historico.transacoes[0]), str))


def executar_testes():
    print()
    print("═" * 50)
    print(f"{'BANCO PYTHON — SUITE DE TESTES':^50}")
    print("═" * 50)

    banco_teste = Banco("Banco de Testes")

    testar_utilitarios()
    testar_cadastro(banco_teste)
    testar_autenticacao(banco_teste)
    testar_operacoes_bancarias(banco_teste)
    testar_transferencias(banco_teste)
    testar_historico(banco_teste)

    total     = len(resultados)
    aprovados = sum(1 for _, ok in resultados if ok)
    reprovados = total - aprovados

    print()
    print("═" * 50)
    print(f"  RESULTADO FINAL: {aprovados}/{total} testes passaram")
    if reprovados > 0:
        print(f"  ⚠️  {reprovados} teste(s) falharam:")
        for nome, ok in resultados:
            if not ok:
                print(f"     → {nome}")
    else:
        print("  🎉 Todos os testes passaram!")
    print("═" * 50)
    print()


if __name__ == "__main__":
    executar_testes()
