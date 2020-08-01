import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from IPython.core.display import display, HTML

sns.set_style('darkgrid')
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'


def checa_valores_bal(df_bal):
    """Checa os valores informados no Balanço para:
        - Total do Ativo
        - Total do Passivo
        - Patrimônio Líquido
    """
    bal = df_bal.copy()

    # Checa o Total do Ativo
    bal.loc['Total do Ativo Calculado'] = \
        (df_bal.loc['Caixa Operacional']
         + df_bal.loc['Caixa Não Operacional']
         + df_bal.loc['Contas a Receber']
         + df_bal.loc['Estoque']
         + df_bal.loc['Ativo Operacional Fixo Líquido'])

    # Checa o Passivo
    bal.loc['Passivo Calculado'] = \
        (df_bal.loc['Contas a Pagar']
         + df_bal.loc['Salários e Encargos a Pagar']
         + df_bal.loc['Impostos a pagar']
         + df_bal.loc['Empréstimos e Financiamentos de CP']
         + df_bal.loc['Empréstimos e Financiamentos de LP'])

    # Checa o Patrimônio Líquido
    bal.loc['PL Calculado'] = (bal.loc['Total do Ativo Calculado']
                               - bal.loc['Passivo Calculado'])

    ativo_ok = np.allclose(bal.loc['Total do Ativo Calculado'],
                           df_bal.loc['Total do Ativo'])
    passivo_ok = np.allclose(bal.loc['Passivo Calculado'],
                             df_bal.loc['Passivo'])
    pl_ok = np.allclose(bal.loc['PL Calculado'],
                        df_bal.loc['Patrimônio Líquido'])

    assert(ativo_ok)
    assert(passivo_ok)
    assert(pl_ok)


def checa_valores_dre(df_dre):
    """Checa os valores informados na DRE para:
        - Resultado Operacional
        - LAIR
        - Lucro Líquido
    """
    dre = df_dre.copy()

    # Checa o Resultado Operacional
    dre.loc['Resultado Operacional Calculado'] = \
        (df_dre.loc['Receita líquida']
         - df_dre.loc['(-) CPV']
         - df_dre.loc['(-) Despesas Operacionais']
         - df_dre.loc['(-) Depreciação'])

    # Checa o Resultado Operacional
    dre.loc['LAIR Calculado'] = \
        (df_dre.loc['(=) Resultado Operacional']
         - df_dre.loc['(-) Despesa Financeira Líquida'])

    # Checa o lucro líquido
    dre.loc['Lucro Líquido Calculado'] = \
        (df_dre.loc['(=) Lucro Antes do IR']
         - df_dre.loc['(-) IR'])

    res_op_ok = np.allclose(dre.loc['Resultado Operacional Calculado'],
                            df_dre.loc['(=) Resultado Operacional'])

    lair_ok = np.allclose(dre.loc['LAIR Calculado'],
                          df_dre.loc['(=) Lucro Antes do IR'])

    ll_ok = np.allclose(dre.loc['Lucro Líquido Calculado'],
                        df_dre.loc['(=) Lucro Líquido'])

    assert res_op_ok
    assert lair_ok
    assert ll_ok


def carrega_dfs(ticker):
    """Carrega os dataframes a partir da planilha de entrada de dados"""
    arq_dados = f'./dados/Dados_Financeiros - {ticker}.xlsx'

    df_dre = pd.read_excel(arq_dados,
                           sheet_name='DRE', header=[0, 1])
    df_bal = pd.read_excel(arq_dados,
                           sheet_name='Balanço', header=[0, 1]).dropna()
    df_par = pd.read_excel(arq_dados,
                           sheet_name='Outras_Entradas', header=[0, 1])

    return df_dre, df_bal, df_par


def carrega_parametros(df_bal, df_par):
    """Obtem parametros de entrada"""

    pars = obtem_parametros(df_par)
    ke_manual = pars['ke']
    kd = pars['kd']
    ir = pars['ir']
    g = pars['g']
    num_acoes = pars['num_acoes']
    cotacao_atual = pars['cotacao']
    tx_desc_manual = pars['tx_desc_manual']
    rf = pars['rf']
    beta = pars['beta']
    premio_risco = pars['premio_risco']
    risco_pais = pars['risco_pais']
    perc_d, perc_e = obtem_estrutura_de_capital(df_bal)

    return ke_manual, kd, ir, g, num_acoes, cotacao_atual, perc_d, perc_e, \
        tx_desc_manual, rf, premio_risco, beta, risco_pais


def obtem_parametros(df_par):
    ke = df_par.loc['Ke Manual'].iloc[0]
    kd = df_par.loc['Kd'].iloc[0]
    g = df_par.loc['G'].iloc[0]
    ir = df_par.loc['IR'].iloc[0]
    num_acoes = df_par.loc['Número de Ações'].iloc[0]
    cotacao = df_par.loc['Cotação atual'].iloc[0]
    rf = df_par.loc['Taxa Livre de Risco (Rf)'].iloc[0]
    premio_risco = df_par.loc['Prêmio de Risco (ERP)'].iloc[0]
    tx_desc_manual = df_par.loc['Taxa de Desconto Manual'].iloc[0]
    beta = df_par.loc['Beta'].iloc[0]
    risco_pais = df_par.loc['Risco País'].iloc[0]

    return {'ke': ke, 'kd': kd, 'g': g, 'ir': ir, 'num_acoes': num_acoes,
            'cotacao': cotacao, 'tx_desc_manual': tx_desc_manual,
            'premio_risco': premio_risco, 'rf': rf, 'beta': beta,
            'risco_pais': risco_pais}


def obtem_info_cg(df_bal):
    """
    Retorna:
    . Capital de Giro do Ativo - CGA
    . Capital de Giro do Passivo - CGP
    . Capital de Giro Líquido - CGL / Necessidade de Capital de Giro) - NCG
    . Investimento em Capital de Giro - ICG / Variação da NCG
    """
    df_cg = pd.DataFrame(columns=df_bal.columns)

    # CGA
    df_cg.loc['Capital de Giro do Ativo'] = \
        (df_bal.loc['Caixa Operacional']
         + df_bal.loc['Contas a Receber']
         + df_bal.loc['Estoque'])

    # CGP
    df_cg.loc['Capital de Giro do Passivo'] = \
        (df_bal.loc['Contas a Pagar']
         + df_bal.loc['Salários e Encargos a Pagar']
         + df_bal.loc['Impostos a pagar'])

    # CGL
    df_cg.loc['Capital de Giro Líquido'] = \
        (df_cg.loc['Capital de Giro do Ativo']
         - df_cg.loc['Capital de Giro do Passivo'])

    # ICG
    df_cg.loc['Investimento em CG'] = \
        df_cg.loc['Capital de Giro Líquido'].diff()

    compoe_mem_calc = [df_bal.loc['Caixa Operacional'],
                       df_bal.loc['Contas a Receber'],
                       df_bal.loc['Estoque'],
                       df_cg.loc['Capital de Giro do Ativo'],
                       df_bal.loc['Contas a Pagar'],
                       df_bal.loc['Salários e Encargos a Pagar'],
                       df_bal.loc['Impostos a pagar'],
                       df_cg.loc['Capital de Giro do Passivo'],
                       df_cg.loc['Capital de Giro Líquido'],
                       df_cg.loc['Investimento em CG']]

    df_memoria_calc_cg = pd.concat(compoe_mem_calc,  axis=1).T

    idx_memoria_calc_cg = ['(+) ..Caixa Operacional',
                           '(+) ..Contas a Receber',
                           '(+) ..Estoque',
                           '(=) Capital de Giro do Ativo',
                           '(+) ..Contas a Pagar',
                           '(+) ..Salários e Encargos a Pagar',
                           '(+) ..Impostos a pagar',
                           '(=) Capital de Giro do Passivo',
                           '(=) => Capital de Giro Líquido',
                           '(=) => Investimento em CG Líquido']

    df_memoria_calc_cg.index = idx_memoria_calc_cg
    return df_cg, df_memoria_calc_cg


def obtem_fluxo_caixa_equity(df_dre, df_bal, df_par, df_cg, taxa_IR=0.34):
    """Obtem o Fluxo de Caixa Operacional para os Investidores =
    + Resultado Operacional
    - Imposto Operacional = RO * (%IR)
    + Depreciação e Amortização
    - CAPEX
    - Investimento em Capital de Giro Líquido

    """
    fcfe = pd.DataFrame(columns=df_cg.columns)
    resultado_operacional = df_dre.loc['(=) Resultado Operacional']
    imposto_operacional = resultado_operacional * taxa_IR
    depreciacao = df_dre.loc['(-) Depreciação']
    amortizacao = 0
    capex = df_par.loc['CAPEX']
    icgl = df_cg.loc['Investimento em CG']

    # FCFE - Free cash Flow to the Equity
    fcfe.loc['FCFE'] = (resultado_operacional
                        - imposto_operacional
                        + depreciacao
                        + amortizacao
                        - capex
                        - icgl
                        )

    df_memoria_calc = pd.concat([resultado_operacional,
                                 -imposto_operacional,
                                 depreciacao,
                                 -capex,
                                 -icgl],  axis=1).T

    index_mem_calc = ['Resultado Operacional',
                      '(-) Imposto Operacional',
                      '(+) Depreciação',
                      '(-) CAPEX',
                      '(-) Investimento em CG Lìquido']

    df_memoria_calc.index = index_mem_calc

    df_memoria_calc.loc['(=) Fluxo de Caixa para o Equity'] = \
        df_memoria_calc.sum()

    return fcfe, df_memoria_calc


def obtem_preco_justo(df_vp, num_acoes):
    valor_presente_equity = float(df_vp.sum())
    valor_justo_por_acao = valor_presente_equity / num_acoes
    return valor_presente_equity, valor_justo_por_acao


def obtem_upside(valor_justo_por_acao, cotacao_atual):
    upside = valor_justo_por_acao / cotacao_atual - 1
    upside_financeiro = (valor_justo_por_acao - cotacao_atual)
    return upside, upside_financeiro


def gera_pares_ano_fc_ano(fcs_projetados):
    """Recebe uma Série de FCs projetados
    Retorna uma lista de tuplas com (ano_i, fluxo_caixa_ano_i)
    Função auxiliar para uso no calculo do valor presente"""

    lista_tuplas = [(i[0] + 1, i[1]) for i in enumerate(fcs_projetados)]

    return lista_tuplas


def gera_valor_presente_fcfe(df_fcf, taxa_desc):
    """Recebe os fluxos de caixa com a perpetuidade
    Retorna os fluxos de caixa projetados ajustados a valor presente
    Retorno feito por referência no próprio DataFrame df_fcf"""

    # gera FCFE_VP e FCFE_VP_Perp
    df_fcf.loc['FCFE_VP'] = 0
    df_fcf.loc['FCFE_Perp_VP'] = 0

    # calcula o valor presente para o FCFE
    for ano, fc in gera_pares_ano_fc_ano(df_fcf.loc['FCFE']['Projetado']):
        rotulo_ano = df_fcf.loc['FCFE']['Projetado'].index[ano-1]
        df_fcf.loc['FCFE_VP']['Projetado', rotulo_ano] = \
            fc / ((1 + taxa_desc) ** ano)

    # calcula o valor presente para a Perpetuidade
    for ano, fc in gera_pares_ano_fc_ano(df_fcf.loc['FCFE_Perp']['Projetado']):
        rotulo_ano = df_fcf.loc['FCFE']['Projetado'].index[ano-1]
        df_fcf.loc['FCFE_Perp_VP']['Projetado', rotulo_ano] = \
            fc / ((1 + taxa_desc) ** ano)

    # Seta Valores do ano atual
    rotulo_ano = df_fcf.loc['FCFE']['Realizado'].index[-1]

    df_fcf.loc['FCFE_VP']['Realizado', rotulo_ano] = \
        df_fcf.loc['FCFE']['Realizado', rotulo_ano]

    df_fcf.loc['FCFE_Perp_VP']['Realizado', rotulo_ano] = \
        df_fcf.loc['FCFE_Perp']['Realizado', rotulo_ano]


def obtem_fcfe_ult_ano_projetado(df_fcf):
    return df_fcf.loc['FCFE']['Projetado'].iloc[-1]


def adiciona_perp_ao_fcfe(df_fcf, fc_perpetuidade):
    """Recebe a perpetuidade e soma
    ao fluxo de caixa do último ano projetado

    Retorna o dataframe com o valor adicinado"""

    ultimo_ano_projetado = df_fcf.columns.levels[1][-1]
    df_fcf.loc['FCFE_Perp'] = 0
    df_fcf.loc['FCFE_Perp']['Projetado', ultimo_ano_projetado] = \
        fc_perpetuidade


def obtem_estrutura_de_capital(df_bal):
    """Retorna a composição de Capital:
    - % D
    - % E
    """
    patrimonio_liquido = df_bal.loc['Patrimônio Líquido']['Realizado'].iloc[-1]
    total_do_passivo = df_bal.loc['Total do Passivo']['Realizado'].iloc[-1]

    perc_e = patrimonio_liquido / total_do_passivo
    perc_d = 1 - perc_e

    return perc_d, perc_e


def obtem_perpetuidade(fc_0, crescimento_g, taxa_desconto):
    """Calcula o valor da Perpetuidade considerando:
    - Fluxo de Caixa do último ano projetado FC_0
    - Taxa de Crescimento na Perpetuidade - G
    - Taxa de Desconto (normalmente, o WACC)

    Retorna o valor equivalente ao ultimo ano projeado"""

    valor_perpetuidade = (fc_0 * (1 + crescimento_g) /
                          (taxa_desconto - crescimento_g))
    return valor_perpetuidade


def obtem_wacc(perc_d, perc_e, ke, kd, taxa_ir):
    """Retorna o WACC"""

    wacc = (ke * perc_e) + (kd * perc_d * (1 - taxa_ir))

    return wacc


def obtem_custo_equity_ke(rf, beta, premio_risco,
                          ke_manual=None, risco_pais=0):

    if(isinstance(ke_manual, float) and ke_manual > 0):
        ke = ke_manual
        str_ke = '(Manual)'
    else:
        ke = rf + risco_pais + beta * (premio_risco)
        str_ke = '(CAPM)'

    return ke, str_ke


# Main Workflow and Reports


def gera_report_dados_entrada(ticker, df_dre, df_bal, df_par):
    imprime_header(f'Dados de Entrada - {ticker}', nivel=2)

    imprime_header('DRE')
    display(df_dre)

    imprime_header('Balanço')
    display(df_bal)

    imprime_header('Outros Parâmetros de Entrada')
    display(df_par)


def gera_report_cg(df_bal, imprime_mem_cal=True):
    imprime_header('Capital de Giro')
    df_cg, df_memoria_calc_cg = obtem_info_cg(df_bal)

    if imprime_mem_cal:
      imprime_rel_mem_calc_icgl(df_memoria_calc_cg)
    return df_cg


def gera_report_fcfe(df_dre, df_bal, df_par, df_cg, ir):
    imprime_header('Fluxo de Caixa Livre para o Equity - FCFE')
    df_fcf, df_memoria_calc = obtem_fluxo_caixa_equity(df_dre, df_bal,
                                                       df_par, df_cg,
                                                       taxa_IR=ir)
    imprime_rel_mem_calc_fcfe(df_memoria_calc)
    gera_plot_fcfe(df_fcf)
    return df_fcf


def gera_report_estr_capital(ticker, df_bal, perc_d, perc_e):
    imprime_header('Estrutura de Capital')

    estrutura_cap = \
        pd.Series(obtem_estrutura_de_capital(df_bal),
                  index=['%D', '%E'], name=f'{ticker}')

    gera_plot_estrutura_capital(df_bal, estrutura_cap)
    imprime_rel_estrutura_capital(perc_e, perc_d)


def gera_report_wacc(perc_d, perc_e, ke, kd, ir, rf,
                     premio_risco, risco_pais, str_ke, beta):

    imprime_header('Calcula o WACC')
    # Calcula o WACC
    wacc = obtem_wacc(perc_d, perc_e, ke, kd, taxa_ir=ir)
    imprime_rel_parametros_wacc(ke, kd, perc_e, perc_d,
                                ir, wacc, rf,
                                premio_risco, risco_pais,
                                str_ke, beta)

    return wacc


def gera_report_perpetuidade(g, df_fcf, wacc, tx_desc_manual, ir):
    imprime_header('Perpetuidade')

    if(isinstance(tx_desc_manual, float) and tx_desc_manual > g):
        taxa_desc = tx_desc_manual
        str_tx_desc = '(Tx Manual)'
    else:
        taxa_desc = wacc
        str_tx_desc = '(WACC)'

    fc_ultimo_ano_proj = obtem_fcfe_ult_ano_projetado(df_fcf)
    fc_perpetuidade = obtem_perpetuidade(fc_ultimo_ano_proj,
                                         crescimento_g=g,
                                         taxa_desconto=taxa_desc)

    imprime_rel_perpetuidade(fc_ultimo_ano_proj, g, ir, taxa_desc,
                             str_tx_desc, fc_perpetuidade=fc_perpetuidade)

    adiciona_perp_ao_fcfe(df_fcf, fc_perpetuidade)
    gera_plot_fcfe_com_perp(df_fcf)

    gera_valor_presente_fcfe(df_fcf, taxa_desc=taxa_desc)
    display(df_fcf[['Projetado']])

    return df_fcf


def gera_report_vp(df_fcf):
    imprime_header('Comparação do FCFE na Perpetuidade vs VP')
    gera_plot_fcfe_com_perp_vp(df_fcf)

    imprime_header('Composição do Valor Presente')
    df_composicao_vp = gera_plot_composicao_valor_presente(df_fcf)

    return df_composicao_vp


def gera_report_valor_justo(df_composicao_vp, num_acoes, cotacao_atual):
    imprime_header('Valor Justo por Ação', nivel=2)

    # Obtem o valor justo projetado para a ação
    valor_presente_equity, valor_justo_por_acao = \
        obtem_preco_justo(df_composicao_vp, num_acoes)

    upside, upside_financeiro = obtem_upside(valor_justo_por_acao,
                                             cotacao_atual)

    imprime_rel_preco_justo(valor_presente_equity,
                            cotacao_atual, num_acoes,
                            valor_justo_por_acao, upside,
                            upside_financeiro)


def gera_relatorio_completo(ticker):

    # Carrega os dados de entrada
    df_dre, df_bal, df_par = carrega_dfs(ticker)

    # Checagem dos dados da DRE e Balanço
    checa_valores_bal(df_bal)
    checa_valores_dre(df_dre)

    # Exibe os dados de entrada
    gera_report_dados_entrada(ticker, df_dre, df_bal, df_par)

    # Carrega parametros de entrada
    ke_manual, kd, ir, g, num_acoes, cotacao_atual, \
        perc_d, perc_e, tx_desc_manual, rf, premio_risco, \
        beta, risco_pais = carrega_parametros(df_bal, df_par)

    # Gera os resultados
    df_cg = gera_report_cg(df_bal)
    df_fcf = gera_report_fcfe(df_dre, df_bal, df_par, df_cg, ir)

    gera_report_estr_capital(ticker, df_bal, perc_d, perc_e)

    ke, str_ke = obtem_custo_equity_ke(rf, beta, premio_risco,
                                       ke_manual=ke_manual,
                                       risco_pais=risco_pais)

    wacc = gera_report_wacc(perc_d, perc_e, ke, kd, ir, rf,
                            premio_risco, risco_pais,
                            str_ke, beta)

    df_fcf_perp = gera_report_perpetuidade(g, df_fcf, wacc,
                                           tx_desc_manual, ir)
    df_composicao_vp = gera_report_vp(df_fcf_perp)

    gera_report_valor_justo(df_composicao_vp, num_acoes, cotacao_atual)


# Plots

def gera_plot_fcfe(df_fcf):
    fig, ax = plt.subplots()
    df_fcf.loc['FCFE'].iloc[1:].plot.bar(title='Fluxo de Caixa para o Equity',
                                         rot=0, color=['darkslategray'],
                                         ax=ax)
    ax.set_title('Fluxo de Caixa para o Equity', fontdict={'fontsize': 15})
    plt.show()


def gera_plot_estrutura_capital(df_bal, estrutura_cap):
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(9, 4))
    cores = {'%D': 'orange', '%E': 'slategray'}
    estrutura_cap.plot.barh(title='Estrutura de Capital',
                            ax=axs[0], color=cores.values())
    estrutura_cap.plot.pie(title='Estrutura de Capital',
                           ax=axs[1], colors=cores.values())
    axs[0].set_title('Estrutura de Capital', fontdict={'fontsize': 15})
    axs[1].set_title('Estrutura de Capital', fontdict={'fontsize': 15})
    plt.show()


def gera_plot_fcfe_com_perp(df_fcf):

    fig, axs = plt.subplots(ncols=2, figsize=(14, 5))
    linhas_perp = ['FCFE', 'FCFE_Perp']

    df_fcf.loc['FCFE'].iloc[1:].plot.bar(rot=0,
                                         color=['darkslategray'],
                                         ax=axs[0])
    df_fcf.loc[linhas_perp].iloc[:, 1:].T.plot.bar(stacked=True,
                                                   rot=0,
                                                   ax=axs[1])

    axs[0].set_title('Fluxo de Caixa para o Equity',
                     fontdict={'fontsize': 15})
    axs[1].set_title('Fluxos de Caixa para o Equity com Perpetuidade',
                     fontdict={'fontsize': 15})

    plt.show()


def gera_plot_fcfe_com_perp_vp(df_fcf):

    fig, axs = plt.subplots(ncols=2, figsize=(14, 5),
                            sharey=True, gridspec_kw={'width_ratios': [1, 1]})
    linhas_perp = ['FCFE', 'FCFE_Perp']
    linhas_perp_vp = ['FCFE_VP', 'FCFE_Perp_VP']

    df_fcf.loc[linhas_perp]['Projetado'].T.plot.bar(stacked=True,
                                                    rot=0, ax=axs[0])
    df_fcf.loc[linhas_perp_vp]['Projetado'].T.plot.bar(stacked=True,
                                                       rot=0, ax=axs[1])

    axs[0].set_title('Fluxos de Caixa para o Equity com Perpetuidade',
                     fontdict={'fontsize': 5})
    axs[1].set_title('FCF Equity com Perpetuidade a Valor Presente',
                     fontdict={'fontsize': 15})

    plt.legend(loc='upper left')

    plt.show()


def gera_plot_composicao_valor_presente(df_fcf):
    fig, ax = plt.subplots(figsize=(10, 2.5))

    df_composicao_vp = \
        pd.DataFrame(df_fcf[df_fcf.index.str.contains('VP')].sum().iloc[1:],
                     columns=[''])

    df_composicao_vp.T.plot.barh(stacked=True, ax=ax)

    ax.set_title('Composição do Valor Presente', fontdict={'fontsize': 15},
                 loc='left')
    ax.legend(loc='upper left', ncol=4)

    plt.show()
    print(df_composicao_vp.T)
    return df_composicao_vp




def imprime_header(texto, nivel=3):
    str_html = f'<h{nivel}>{texto}</h{nivel}>'
    display(HTML(str_html))


def imprime_rel_estrutura_capital(perc_e, perc_d):
    print(f'-------------------------------------')
    print(f' Estrutura de Capital:')
    print(f'-------------------------------------')
    print(f' %E   = {100*perc_e:4.1f}%')
    print(f' %D   = {100*perc_d:4.1f}%')
    print(f'-------------------------------------')


def imprime_rel_parametros_wacc(ke, kd, perc_e, perc_d, ir, wacc,
                                rf, premio_risco, risco_pais,
                                str_ke, beta):

    print(f'-------------------------------------')
    print(f' Cálculo do WACC:')
    print(f'-------------------------------------')
    print(f' Ke   = {100*ke:4.1f}% {str_ke}\tRpais= {100*risco_pais:4.1f}%')
    print(f' %E   = {100*perc_e:4.1f}%\t\tBeta = {beta:4.1f}')
    print(f' Rf   = {100*rf:4.1f}%\t\tERP  = {100*premio_risco:4.1f}%')
    print(f' Kd   = {100*kd:4.1f}%\t\tIR   = {100*ir:4.1f}%')
    print(f' %D   = {100*perc_d:4.1f}%\t\t'
          + BOLD + f'WACC = {100*wacc:4.1f}%' + END)
    print(f'-------------------------------------')


def imprime_rel_perpetuidade(fc_ultimo_ano_proj, g, ir, taxa_desc,
                             str_tx_desc, fc_perpetuidade):

    print(f'-------------------------------------')
    print(f' Perpetuidade:')
    print(f'-------------------------------------')
    print(f' FC_0    = R$ {fc_ultimo_ano_proj:7.2f}')
    print(f' G       = {100 * g:9.1f}%')
    print(f' i       = {100 * taxa_desc:9.1f}% {str_tx_desc}')
    print(f' IR      = {100 * ir:9.1f}%')
    print(BOLD + f' FC_perp = R$ {fc_perpetuidade:7.2f}' + END)
    print(f'-------------------------------------')


def imprime_rel_mem_calc_icgl(df_cg):
    print('---------------------------------------------------------------')
    print(' Memória de Cálculo do Investimento em Capital de Giro Líquido:')
    print('---------------------------------------------------------------')
    print(df_cg)


def imprime_rel_mem_calc_fcfe(df_memoria_calc_fcfe):
    print('----------------------------')
    print(' Memória de Cálculo do FCFE:')
    print('----------------------------')
    print(df_memoria_calc_fcfe)


def imprime_rel_preco_justo(valor_presente_equity, cotacao_atual,
                            num_acoes, valor_justo_por_acao,
                            upside, upside_financeiro):
    print(f'-----------------------------------------')
    print(f' Valuation:')
    print(f'-----------------------------------------')
    print(f' Valor Presente do Equity = R$ {valor_presente_equity:8.2f}')
    print(f'-----------------------------------------')
    print(f' Número de Ações          = {int(num_acoes):} ações')
    print(f' Cotação atual            = R$ {cotacao_atual:8.2f}')
    print(f'=========================================')
    print(BOLD + f' Valor Justo por Ação     = R$ {valor_justo_por_acao:8.2f}'
          + END)
    print(f'-----------------------------------------')
    print(BOLD + f' Upside projetado         = {100 * upside:10.2f}%' + END)
    print(BOLD + f' Upside proj por Ação     = R$ {upside_financeiro:8.2f}'
          + END)
    print(f'=========================================')

