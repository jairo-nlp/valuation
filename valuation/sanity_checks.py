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