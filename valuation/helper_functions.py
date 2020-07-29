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
    fc_ult_ano_proj = df_fcf.loc['FCFE']['Projetado'].iloc[:-1]
    fc_combinado_perp = fc_ult_ano_proj + fc_perpetuidade

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