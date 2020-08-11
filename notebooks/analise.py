# Classe análise

import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
from itertools import combinations
from pandas_datareader.data import DataReader
from datetime import date

class Analise():

    def _gera_lista_tickers(self):
        self.tickers = []
        for (setor, tickers_setor) in self.setores_tickers.items():
            self.tickers.extend(tickers_setor)

    def __init__(self, ativos, data_ini, data_fim):
        """Análise de setores e ativos.

        :param ativos: Dicionário da forma
        {'setor1': ['ticker1', 'ticker2', ...],
         'setor2': ['ticker3', 'ticker4', ...],
         ...
         'setorN': ['tickerM', ...]
        }
        :param data_ini: data de inicio da analise
        :param data_fim: data de final da analise
        """

        self.dados = {}
        self.setores_tickers = ativos

        self.setores = list(self.setores_tickers.keys())
        self.num_setores = len(self.setores)
        self.TAB_COLORS = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:pink', 'tab:olive', 'tab:cyan']
        self.cores = {setor: self.TAB_COLORS[idx % len(self.TAB_COLORS)]
                      for idx, setor in enumerate(self.setores)}

        self.data_ini = pd.to_datetime(data_ini)
        self.data_fim = pd.to_datetime(data_fim)

        self._gera_lista_tickers()

    
    def __str__(self):
        msg_ret = ('Ativos:\n' + str(self.setores_tickers)
                   + '\nData Inicial:\t' + self.data_ini.strftime('%m/%Y')
                   + '\nData Final:\t' + self.data_fim.strftime('%m/%Y')
        )

        return msg_ret
    
    def obtem_dados_setores(self):
        """Retorna df com dados das ações do setor informado
        """
        data_source = 'yahoo'
        for setor in self.setores:
            dados_precos = DataReader(self.setores_tickers[setor],
                                      data_source,
                                      self.data_ini,
                                      self.data_fim)
            self.dados[setor] = dados_precos[['Adj Close']]


    def normalizado(self, df):
        """Normaliza dados gerando o efeito de começarem todos em 1.

        Para integrar ao dataframe original, use o append.

        Ex: df.append(normalizado(df))

        :param df: dataframe de entrada com n ativos em multiindex
        :return df_norm: dataframe de saída, com a coluna normalizada mantendo o índice dos ativos, porém utilizando 'Norm Close' para o nível mais acima.
        """
        tickers = df.columns.levels[1]
        names = df.columns.names
        idx = df.index
        cols = pd.MultiIndex.from_product([['Norm Close'], tickers], names=names)

        return pd.DataFrame((df['Adj Close'] / (df['Adj Close'].iloc[0])).values, columns=cols, index=idx)
    
    def obtem_tickers_legenda(self, legend_labels):
        filtro_rotulos = r'\,\s(.*)\.'
        rotulos_amigaveis = [re.findall(filtro_rotulos, el)[0] 
                            for el in legend_labels]
        return rotulos_amigaveis

    def plot_linhas(self, df, setor=''):
        """Gera um gráfico das cotações das ações de um setor.
        :param df: dataframe com os dados de cotação normalizada
        :param setor: nome do setor
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        df.plot(ax=ax)
        plt.xlabel('Tempo')
        plt.ylabel('Cotação')

        # Para incluir no título do gráfico
        data_ini = df.index[0].strftime('%m/%Y')
        data_fim = df.index[-1].strftime('%m/%Y')

        legend_labels = ax.get_legend_handles_labels()[1]
        ax.legend(self.obtem_tickers_legenda(legend_labels))

        plt.title(f'Cotação Relativa - {setor.upper()} - ({data_ini} - {data_fim})')
        plt.show()


    def plot_linhas_compara_setores(self, dados, highlights=None):
        """Gera um gráfico das cotações das ações de um setor.
        :param dados: dataframe com os dados de cotação normalizada
        :param setores: lista de setores
        :param cores: dicionário de cores por setor
        :param highlights: lista de setores a destacar
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        for setor in self.setores:
            df_setor = self.dados[setor]['Norm Close']
          
            # destaca setor(es) na lista de highlights
            if setor in highlights:
                alpha = 1
            else:
                alpha = 0.2

            df_setor.plot(ax=ax, color=self.cores[setor], alpha=alpha)

        plt.xlabel('Tempo')
        plt.ylabel('Cotação')

        # Para incluir no título do gráfico
        data_ini = df_setor.index[0].strftime('%m/%Y')
        data_fim = df_setor.index[-1].strftime('%m/%Y')

        legend_labels = ax.get_legend_handles_labels()[1]
        ax.legend(legend_labels)

        plt.title(f'Cotação Relativa - {str(highlights).upper()} - ({data_ini} - {data_fim})')
        plt.show()


    def corrige_agrupamento(self, ticker, multiplicador, data_ant):
        """Corrige um agrupamento para trás da data

        :param ticker: ticker da ação a corrigir
        :param multiplicador: multiplicador do agrupamento
        :param data_ant: data do último dia de cotação antes do grupamento
        """
        # Procura em todos os dfs quais possuem o ticker que passou por agrupamento
        # caso possua o ticker, corrige
        for setor in self.setores_tickers.keys():
            possui_ticker = ticker in self.setores_tickers[setor]
            if possui_ticker:
                # Corrige os dados conforme o multiplicador
                self.dados[setor].loc[:data_ant, [('Adj Close', ticker)]] = (
                    multiplicador * 
                    self.dados[setor].loc[:data_ant, [('Adj Close', ticker)]]
                )


    def analise_intrasetorial(self, setores=None):
        dados = {}
        if setores is None:
            setores = self.setores
      
        self.obtem_dados_setores()

        if 'TCSA3.SA' in self.tickers:
            self.corrige_agrupamento('TCSA3.SA', 10,
                                     data_ant=pd.to_datetime('2020-5-25'))

        # Gera gráficos 
        for setor in setores:
            dados_normalizados = self.normalizado(self.dados[setor])
            self.dados[setor] = pd.concat([self.dados[setor], dados_normalizados], axis=1)
            self.plot_linhas(dados_normalizados, setor=setor)


    def analise_intersetorial(self):
        for par_de_setores in combinations(self.setores, 2):
            self.plot_linhas_compara_setores(self.dados, highlights=par_de_setores)
