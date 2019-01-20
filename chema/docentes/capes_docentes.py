# -*- coding: utf-8 -*-
import errno
import os
import sys
import pandas as pd
import codecs
import csv
import commands
import datetime

from settings import BASE_PATH_DATA
from utils.utils import *

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, '../../../buscador_scripts/')

class CapesDocentes(object):
    """
    A classe CapesDocentes é responsável pela transformaçao da base de dados(Collection - docentes),
    faz parte do processo de ETL(Extração, Transformação e Carga).

    Atributos:
        date            (date): data de execução deste arquivo.
        input_lenght    (int): Variável que irá guardar a quantidade de linhas do arquivo de entrada(download).
        output_length   (int): Variável que irá guardar a quantidade de linhas do arquivo de saída(transform).
        colunas         (dic): Dicionário das colunas do arquivo csv.

    """

    def __init__(self, arquivos, nome_arquivo):
        """
        Construtor da classe CapesDocentes, necessita de 2 parâmetros:
        arquivos        (list): Lista com todos os arquivos da pasta download -  BASE_PATH_DATA + 'capes/docentes/download/'.
        nome_arquivo    (str): Nome dos arquivos da pasta download BASE_PATH_DATA + 'capes/docentes/download/'.

        """

        self.date = datetime.datetime.now()
        self.arquivos = arquivos
        self.nome_arquivo = nome_arquivo
        self.input_lenght = 0
        self.output_length = 0
        self.arq_prog = self.pega_arquivo_programas_download()
        self.cadastro_ies = self.pega_arquivo_cadastro_ies_capes()

        self.colunas = [
            'AN_BASE',
            'NM_GRANDE_AREA_CONHECIMENTO',
            'CD_AREA_AVALIACAO',
            'NM_AREA_AVALIACAO',
            'SG_ENTIDADE_ENSINO',
            'NM_ENTIDADE_ENSINO',
            'CS_STATUS_JURIDO',
            'DS_DEPENDENCIA_ADMINISTRATIVA',
            'NM_MODALIDADE_PROGRAMA',
            'NM_GRAU_PROGRAMA',
            'CD_PROGRAMA_IES',
            'NM_PROGRAMA_IES',
            'NM_REGIAO',
            'SG_UF_PROGRAMA',
            'NM_MUNICIPIO_PROGRAMA_IES',
            'CD_CONCEITO_PROGRAMA',
            'CD_CONCEITO_CURSO',
            'ID_PESSOA',
            'NM_DISCENTE',
            'NM_PAIS_NASCIONALIDADE_DISCENTE',
            'DS_TIPO_NACIONALIDADE_DISCENTE',
            'TP_SEXO_DISCENTE',
            'DS_FAIXA_ETARIA',
            'DS_GRAU_ACADEMICO_DISCENTE',
            'ST_INGRESSANTE',
            'NM_SITUACAO_DISCENTE',
            'DT_MATRICULA_DISCENTE',
            'DT_SITUACAO_DISCENTE',
            'QT_MES_TITULACAO',
            'NM_TESE_DISSERTACAO',
            'NM_ORIENTADOR',
            'ID_ADD_FOTO_PROGRAMA',
            'ID_ADD_FOTO_PROGRAMA_IES',
            'NR_DOCUMENTO_DISCENTE',
            'TP_DOCUMENTO_DISCENTE',

        ]

    def pega_arquivos_docentes(self):
        ''' Pega os arquivos em docentes/download, conta as linhas de entrada do arquivo,
            adiciona cada arquivo na lista(df_auxiliar), faz a concatenação deles e os retorna

        '''

        var = BASE_PATH_DATA + 'capes/docentes/download/'
        df_auxiliar = []
        for root, dirs, files in os.walk(var):
            for file in files:
                if file in self.arquivos:
                    arquivo = codecs.open(os.path.join(root, file), 'r')  # , encoding='latin-1')
                    self.input_lenght += int(
                        commands.getstatusoutput('cat ' + os.path.join(root, file) + ' |wc -l ')[1])
                    print 'Arquivo de entrada possui {} linhas de informacao'.format(int(self.input_lenght) - 1)
                    df_auxiliar.append(pd.read_csv(arquivo, sep=';', low_memory=False, encoding='cp1252'))
                    #df_auxiliar = pd.read_csv(arquivo, sep=';', nrows=3000, chunksize=3000, encoding='latin-1', low_memory=False)
        #import pdb;pdb.set_trace()  #para testar o código

        df_docentes = pd.concat(df_auxiliar)
        # renomeia para corrigir o erro de merge com programas e instituições
        df_docentes.replace('FUNDACAO OSWALDO CRUZ', 'FUNDACAO OSWALDO CRUZ (FIOCRUZ)', inplace=True)
        # cria a coluna no dataframe docentes para o merge com programas e instituições
        df_docentes['SG_ENTIDADE_ENSINO_Capes'] = df_docentes['SG_ENTIDADE_ENSINO']
        df_docentes['NM_ENTIDADE_ENSINO_Capes'] = df_docentes['NM_ENTIDADE_ENSINO']

        # remover a coluna que irão gerar conflito com instituições,
        df_docentes = df_docentes.drop(['DS_DEPENDENCIA_ADMINISTRATIVA','CS_STATUS_JURIDICO'], axis=1)

        return df_docentes


    def pega_arquivo_programas_download(self):
        """Pega os arquivos do diretorio capes/programas, faz um append deles e os retorna"""

        var = BASE_PATH_DATA + 'capes/programas/download/'
        df_auxiliar = []
        print 'Lendo os arquivos do CAPES programas....'
        for root, dirs, files in os.walk(var):

            for file in files:
                print file
                arquivo = codecs.open(os.path.join(root, file), 'r')  # , encoding='latin-1')
                self.input_lenght += int(commands.getstatusoutput('cat ' + os.path.join(root, file) + ' |wc -l ')[1])
                print 'Arquivo de entrada possui {} linhas de informacao'.format(int(self.input_lenght) - 1)
                df_auxiliar.append(pd.read_csv(arquivo, sep=';', low_memory=False, encoding='cp1252'))
                #df_auxiliar = pd.read_csv(arquivo, sep=';', nrows=10000, chunksize=1000, encoding='cp1252', low_memory=False)

        df_programas = pd.concat(df_auxiliar, sort=False)
        # drop de algumas colunas de programas que geram duplicidade com docentes
        df_programas = df_programas.drop(['NM_GRANDE_AREA_CONHECIMENTO', 'NM_AREA_CONHECIMENTO','CD_AREA_AVALIACAO',
        'NM_AREA_AVALIACAO', 'SG_ENTIDADE_ENSINO', 'NM_ENTIDADE_ENSINO', 'CS_STATUS_JURIDICO',
        'DS_DEPENDENCIA_ADMINISTRATIVA','NM_REGIAO', 'NM_MUNICIPIO_PROGRAMA_IES', 'NM_MODALIDADE_PROGRAMA',
        'NM_PROGRAMA_IES', 'SG_UF_PROGRAMA', 'NM_GRAU_PROGRAMA', 'CD_CONCEITO_PROGRAMA',
        'ID_ADD_FOTO_PROGRAMA_IES', 'ID_ADD_FOTO_PROGRAMA'], axis=1)

        return df_programas


    def pega_arquivo_cadastro_ies_capes(self):
        """pega os arquivos de cadastro CAPES IES que serão agregados aos Discentes"""

        var = '/var/tmp/solr_front/collections/capes/instituicoes/download'
        for root, dirs, files in os.walk(var):
            for file in files:
                arquivo = codecs.open(os.path.join(root, file), 'r')  # , encoding='latin-1')
                df_cad_temp = pd.read_csv(arquivo, sep=';', low_memory=False, encoding='latin-1')
        # eliminando as colunas vazias do csv.
        df_cad_ies = df_cad_temp.dropna(how = 'all', axis = 'columns')
        df_cad_ies = df_cad_ies.dropna(how = 'all', axis = 'rows')
        # ----- DELETANDO O AN_BASE E DS_DEPENDENCIA_ADMINISTRATIVA PARA NÃO GERAR DUAS COLUNAS IGUAIS APÓS O MERGE ------
        df_cad_ies = df_cad_ies.drop(['AN_BASE'], axis=1)

        return df_cad_ies

    def merge_dataframes(self, df):
        ''' Colunas que serão agregadas aos Docentes, segundo o modelo. Esta função
            recebe um dataframe de parametro e faz o merge dele com os arquivos
            do CAPES Programas.'''

        print 'Fazendo o merge......'
        df_merg_doc_prog = df.merge(self.arq_prog, on=['AN_BASE', 'CD_PROGRAMA_IES'],suffixes=('_docentes', '_programas'))

        return df_merg_doc_prog

    def resolve_dicionarios(self):
        """
        Pega o Dataframe de retorno do método pega_arquivos_docentes, resolve os campos para facet
        e os retorna para o gera_csv.

        """
        df = self.pega_arquivos_docentes()
        df = self.merge_dataframes(df)
        # df == df_merg_doc_prog neste ponto

        df = df.merge(self.cadastro_ies, on=['SG_ENTIDADE_ENSINO_Capes','NM_ENTIDADE_ENSINO_Capes'],suffixes=('_docentes', '_institu'))

        # Lista com as datas que devem ser formatadas
        parse_dates = ['DT_SITUACAO_PROGRAMA']

        for dt in parse_dates:
            # Percorre a lista de datas e seta o formato da data que o datetime usará para a conversão, ou seja,
            # a máscara do formato.
            df[dt] = pd.to_datetime(df[dt], infer_datetime_format=False, format='%d%b%Y:%H:%M:%S', errors='coerce')

        # para ordenar a data para o facet
        linha_SITUACAO_PROGRAMA = []
        df['DT_SITUACAO_PROGRAMA'] = df[dt].dt.strftime('%Y%m%d')
        for row in df['DT_SITUACAO_PROGRAMA'].sort_values(ascending=False).astype(str):
            linha_SITUACAO_PROGRAMA.append(row)
        # criando um dataframe com a coluna DT_MATRICULA_DISCENTE ordenada
        dt_order = pd.DataFrame({'DT_SITUACAO_PROGRAMA_order':linha_SITUACAO_PROGRAMA})
        # fazendo o join com o dataframe principal(df)
        df = df.join(dt_order)
        df['DT_SITUACAO_PROGRAMA_order'] = df['DT_SITUACAO_PROGRAMA_order'].apply(data_facet)

        #df.sort_values(by='Idade', ascending=True)
        df['ID_PESSOA'] = df['ID_PESSOA'].astype(str)
        df['AN_TITULACAO'] = df['AN_TITULACAO'].astype(int)
        df['AN_BASE_facet'] = df['AN_BASE'].apply(gYear)
        df['NM_REGIAO_facet'] = df['NM_REGIAO'] + '|' + df['SG_UF_PROGRAMA'] + '|' + df['NM_MUNICIPIO_PROGRAMA_IES']

        # Campos setados do cadastro CAPES IES
        df['cat_insti'] = df['Tipo_de_Instituicao']
        df['CS_Natureza_Juridica'] = df['Nome_Natureza_Juridica-GEI']
        df['DS_ORGANIZACAO_ACADEMICA_Fapesp'] = df['DS_ORGANIZACAO_ACADEMICA-GEI']

        # campos de busca
        df['NM_PROGRAMA_IES_exact'] = df['NM_PROGRAMA_IES']
        df['CD_PROGRAMA_IES_exact'] = df['CD_PROGRAMA_IES'].astype(str)
        df['ID_PESSOA_exact'] = df['ID_PESSOA']
        df['CD_AREA_BASICA_TITULACAO_exact'] = df['CD_AREA_BASICA_TITULACAO'].astype(str)

        #df['INSTITUICAO_ENSINO_facet'] =  df['SG_ENTIDADE_ENSINO'] + '|' + df['NM_ENTIDADE_ENSINO']
        # CAMPOS PARA BUSCA AVANÇADA
        # df['NM_PROGRAMA_IES_exact'] = df['NM_PROGRAMA_IES']
        # df['NM_PROGRAMA_IDIOMA_exact'] = df['NM_PROGRAMA_IDIOMA']
        # df[u'NM_TESE_DISSERTACAO_exact'] = df[u'NM_TESE_DISSERTACAO'].apply(norm_keyword)
        # df['ID_PESSOA_exact'] = df['ID_PESSOA']
        # df['CD_PROGRAMA_IES_exact'] = df['CD_PROGRAMA_IES']
        # df['NM_ORIENTADOR_exact'] = df['NM_ORIENTADOR'].apply(norm_keyword)

        print 'df pronto para gerar'
        import pdb; pdb.set_trace()

        return df

    def gera_csv(self):
        """
        Pega o Dataframe de retorno do método resolve_dicionario, cria o diretório de destino,
        conta as linhas do arquivo de saída e grava o .csv e o .log no diretório de destino.

        """

        df_capes = self.resolve_dicionarios()

        destino_transform = BASE_PATH_DATA + 'capes/docentes/transform'
        csv_file = '/capes_' + self.nome_arquivo + '.csv'
        log_file = '/capes_' + self.nome_arquivo + '.log'

        try:
            os.makedirs(destino_transform)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        df_capes.to_csv(destino_transform + csv_file, sep=';', index=False, encoding='utf8',
                        line_terminator='\n', quoting=csv.QUOTE_ALL)
        self.output_length = commands.getstatusoutput('cat ' + destino_transform + csv_file + ' |wc -l')[1]
        print 'Arquivo de saida possui {} linhas de informacao'.format(int(self.output_length) - 1)

        with open(destino_transform + log_file, 'w') as log:
            log.write('Log gerado em {}'.format(self.date.strftime("%Y-%m-%d %H:%M")))
            log.write("\n")
            log.write('Arquivo de entrada possui {} linhas de informacao'.format(self.input_lenght))
            log.write("\n")
            log.write('Arquivo de saida possui {} linhas de informacao'.format(int(self.output_length) - 1))
        print('Processamento CAPES {} finalizado, arquivo de log gerado em {}'.format(self.nome_arquivo,
                                                                                      (destino_transform + log_file)))

def capes_docentes_transform():
    """
    Função chamada em transform.py para ajustar os dados da  CAPES Docentes e prepará-los
    para a carga no indexador. Seta o diretorio onde os arquivos a serem transformados/ajustados estão,
    e passa os parâmetros - arquivos e nome_arquivo para a classe CapesDocentes.

    """

    PATH_ORIGEM = BASE_PATH_DATA + 'capes/docentes/download'

    try:
        arquivos = os.listdir(PATH_ORIGEM)
        arquivos.sort()
        arquivo_inicial = arquivos[0]
        nome_arquivo = arquivo_inicial.split('_')[0]
        capes_doc = CapesDocentes(arquivos, nome_arquivo)
        capes_doc.gera_csv()
        print('Arquivo {} finalizado!'.format(nome_arquivo))

    except OSError:
        print('Nenhum arquivo encontrado')
        raise
