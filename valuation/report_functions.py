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


def gera_report_estr_capital(df_bal, perc_d, perc_e):
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
        obtem_preco_justo(df_composicao_vp)

    upside, upside_financeiro = obtem_upside(valor_justo_por_acao,
                                             cotacao_atual, num_acoes)

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

    gera_report_estr_capital(df_bal, perc_d, perc_e)

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
