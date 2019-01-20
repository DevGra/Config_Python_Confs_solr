# -*- coding: utf-8 -*-
import errno
import os
import sys

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, '../../../buscador_scripts/')

from utils.utils import *
import pandas as pd
import codecs
import csv
import commands
from datetime import datetime


class CapesInstituicoes(object):
    """
    A classe CapesInstituicoes é responsável pela transformaçao da base de dados(Collection - Instituições),
    faz parte do processo de ETL(Extração, Transformação e Carga).

    Atributos:
        date            (datetime): data de execução deste arquivo.
        input_lenght    (int): Variável que irá guardar a quantidade de linhas do arquivo de entrada(download).
        output_length   (int): Variável que irá guardar a quantidade de linhas do arquivo de saída(transform).
        ies             (class: pandas.core.frame.DataFrame): Dataframe dos arquivos de download da capes cadastro IES, em BASE_PATH_DATA + 'capes/programas/cadastro/'.
        colunas         (dict): Dicionário das colunas do arquivo csv - programas.

    """

    def __init__(self, arquivo, nome_arquivo):
        """
        Construtor da classe CapesInstituicoes, recebe 2 parâmetros.

        PARAMETROS:
            arquivos        (list): Lista com todos os arquivos da pasta download -  BASE_PATH_DATA + 'capes/programas/download/'.
            nome_arquivo    (str): Nome dos arquivos da pasta download BASE_PATH_DATA + 'capes/programas/download/'.

        """
        self.date = datetime.now()
        self.arquivos = arquivo
        self.nome_arquivo = nome_arquivo
        self.input_lenght = 0
        self.output_length = 0
        self.colunas = [
            "AN_BASE",
            "SG_ENTIDADE_ENSINO_Capes",
            "NM_ENTIDADE_ENSINO_Capes",
            "CD_INST_GEI",
            "SG_INST_GEI",
            "NM_INST_GEI",
            "CAT_INST",
            "CS_STATUS_JURIDICO",
            "DS_DEPENDENCIA_ADMINISTRATIVA",
            "CS_Natureza_Juridica",
            "DS_ORGANIZACAO_ACADEMICA_Fapesp-GEI",
            "DS_ORGANIZACAO_ACADEMICA_CAPES",
            "CD_Mantenedora",
            "NM_Mantenedora",

        ]

    def pega_arquivo_nome(self):
        """
        Este método itera os arquivos em: BASE_PATH_DATA + 'capes/instituicoes/download/'
        e conta suas as linhas.

        PARAMETRO:
            Não recebe parâmetro.

        RETORNO:
            Retorna o df_auxiliar, que é um TextFileReader da classe pandas.io.parses.TextFileReader

        """

        var = '/var/tmp/solr_front/collections/capes/instituicoes/download/'

        for root, dirs, files in os.walk(var):
            for file in files:
                arquivo = codecs.open(os.path.join(root, file), 'r')  # , encoding='latin-1')
                df_cad_temp = pd.read_csv(arquivo, sep=';', low_memory=False, encoding='latin-1')
        # eliminando as colunas vazias do csv.
        df_cadastro_ies = df_cad_temp.dropna(how = 'all', axis = 'columns')
        df_cadastro_ies = df_cadastro_ies.dropna(how = 'all', axis = 'rows')

        # df_duplic = df_cad.duplicated(['NM_ENTIDADE_ENSINO_Capes'])
        # df_true = 0
        # if df_duplic == True:
        #     df_true = df_duplic
        #import pdb; pdb.set_trace()
        return df_cadastro_ies


    def resolve_dicionarios(self):

        df = self.pega_arquivo_nome()

        # Campos setados do cadastro CAPES IES
        df['cat_insti'] = df['Tipo_de_Instituicao']
        df['CS_Natureza_Juridica'] = df['Nome_Natureza_Juridica-GEI']
        df['NM_INST_FapespGei'] = df['NM_INST_Gei']
        df['DS_ORGANIZACAO_ACADEMICA_Fapesp'] = df['DS_ORGANIZACAO_ACADEMICA-GEI']

        import pdb; pdb.set_trace()
        return df

    def gera_csv(self):
        """
        Método recebe o retorno do método resolve_dicionario,
        cria os arquivos de saída(.csv e .log) e o diretório de destino,
        conta as linhas do arquivo .csv e os grava no diretório de destino.

        PARAMETRO:
            Não recebe parâmetro.

        RETORNO:
            Método sem retorno, mostra apenas uma mensagem de processamento finalizado.

        """

        df_capes = self.resolve_dicionarios()

        destino_transform = '/var/tmp/solr_front/collections/capes/programas/transform'
        csv_file = '/capes_programas_' + self.nome_arquivo + '.csv'
        log_file = '/capes_programas_' + self.nome_arquivo + '.log'

        try:
            os.makedirs(destino_transform)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        df_capes.to_csv(destino_transform + csv_file, sep=';', index=False, encoding='utf8') #'line_terminator='\n', quoting=csv.QUOTE_ALL)
        self.output_length = commands.getstatusoutput('cat' + destino_transform + csv_file + ' |wc -l')[1]
        print 'Arquivo de saida possui {} linhas de informacao'.format(int(self.output_length) - 1)

        with open(destino_transform + log_file, 'w') as log:
            log.write('Log gerado em {}'.format(self.date.strftime("%Y-%m-%d %H:%M")))
            log.write("\n")
            log.write('Arquivo de entrada possui {} linhas de informacao'.format(int(self.input_lenght) - 1))
            log.write("\n")
            log.write('Arquivo de saida possui {} linhas de informacao'.format(int(self.output_length) - 1))
        print('Processamento CAPES PROGRAMAS {} finalizado, arquivo de log gerado em {}'.format(self.nome_arquivo, (destino_transform + log_file)))

def capes_programas_transform():
    """
    Função chamada em transform.py para ajustar os dados da Capes Programas e prepará-los
    para a carga no indexador. Seta o diretório onde os arquivos a serem transformados/ajustados estão,
    passa os parâmetros - arquivo e nome_arquivo para a classe CapesInstituicoes.

    PARAMETRO:
        Não recebe parâmetro.

    RETORNO:
        Função sem retorno.

    """

    PATH_ORIGEM = '/var/tmp/solr_front/collections/capes/instituicoes/download'
    try:
        arquivos = os.listdir(PATH_ORIGEM)
        arquivos.sort()
        # tamanho_arquivo = len(arquivos) - 1
        # arquivo_inicial = arquivos[0].split('.')[0]
        # arquivo_final = arquivos[tamanho_arquivo].split('.')[0]
        # nome_arquivo = arquivo_inicial +'_a_'+ arquivo_final
        for arquivo in arquivos:
            nome_arquivo = arquivo.split('.')[0]
            capes_doc = CapesInstituicoes(arquivo, nome_arquivo)
            capes_doc.gera_csv()
        print('Arquivo {} finalizado!'.format(arquivo))

    except OSError:
        print('Nenhum arquivo encontrado')
        raise
