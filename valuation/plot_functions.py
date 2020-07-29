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