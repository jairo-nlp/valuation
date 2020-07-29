

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


