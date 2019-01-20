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
# Imports para acrescentar ao programas o cadastro das CAPES
#from dicionarios.cod_gei import cod_gei_dic
#from dicionarios.cod_mantenedora import cod_mantenedora_dic
#from dicionarios.cod_oorgani_acad_gei import cod_org_acad_gei_dic
#from dicionarios.cod_tipo_institu import cod_tipo_institu_dic
#from dicionarios.nat_juridica_gei import nat_jurudica_gei_dic


class CapesProgramas(object):
    """
    A classe CapesProgramas é responsável pela transformaçao da base de dados(Collection - programas),
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
        Construtor da classe CapesProgramas, recebe 2 parâmetros.

        PARAMETROS:
            arquivos        (list): Lista com todos os arquivos da pasta download -  BASE_PATH_DATA + 'capes/programas/download/'.
            nome_arquivo    (str): Nome dos arquivos da pasta download BASE_PATH_DATA + 'capes/programas/download/'.

        """
        self.date = datetime.now()
        self.arquivos = arquivo
        self.nome_arquivo = nome_arquivo
        self.input_lenght = 0
        self.output_length = 0
        self.ies = self.pega_arquivo_cadastro_ies_capes()
        self.colunas = [
            'AN_BASE',
            'ID_PESSOA',
            'NM_DISCENTE',
            'TP_DOCUMENTO_DISCENTE',
            'NR_DOCUMENTO_DISCENTE',
            'SituacaoDiscente',
            'IngressanteAno',
            'GrauAcademico',
            'DT_SITUACAO_DISCENTE',
            'Ano_SITUACAO_DISCENTE',
            'DT_MATRICULA_DISCENTE',
            'Ano_SITUACAO_MATRICULA',
            'DT_TITULACAO',
            'QT_MES_TITULACAO',
            'Casos_excluidos_GeoCapes',
            'Genero',
            'Idade',
            'DS_TIPO_NACIONALIDADE_DISCENTE',
            'NM_PAIS_NACIONALIDADE_DISCENTE',
            'NM_INST_FapespGei',
            'SG_ENTIDADE_ENSINO',
            'NM_ENTIDADE_ENSINO',
            'cat_insti',
            'CS_STATUS_JURIDICO',
            'DS_DEPENDENCIA_ADMINISTRATIVA',
            'CS_Natureza_Juridica',
            'DS_ORGANIZACAO_ACADEMICA_Fapesp',
            'NM_REGIAO',
            'SG_UF_PROGRAMA',
            'NM_MUNICIPIO_PROGRAMA_IES',
            'CD_PROGRAMA_IES',
            'NM_PROGRAMA_IES',
            'NM_GRANDE_AREA_CONHECIMENTO',
            'NM_AREA_CONHECIMENTO',
            'NM_AREA_BASICA',
            'NM_SUBAREA_CONHECIMENTO',
            'NM_ESPECIALIDADE',
            'CD_AREA_AVALIACAO',
            'NM_AREA_AVALIACAO',
            'CD_CONCEITO_PROGRAMA',
            'CD_CONCEITO_CURSO',
            'NM_MODALIDADE_PROGRAMA',
            'NM_GRAU_PROGRAMA',
            'IN_REDE',
            'DS_SITUACAO_PROGRAMA',
            'DT_SITUACAO_PROGRAMA',
            'NM_TESE_DISSERTACAO',
            'NM_ORIENTADOR',
            'ID_ADD_FOTO_PROGRAMA',
            'ID_ADD_FOTO_PROGRAMA_IES'

        ]

    def pega_arquivo_nome(self):
        """
        Este método itera os arquivos em: BASE_PATH_DATA + 'capes/programas/download/'
        e conta suas as linhas.

        PARAMETRO:
            Não recebe parâmetro.

        RETORNO:
            Retorna o df_auxiliar, que é um TextFileReader da classe pandas.io.parses.TextFileReader

        """

        var = '/var/tmp/solr_front/collections/capes/programas/download/'
        df_auxiliar = []
        for root, dirs, files in os.walk(var):
            for file in files:
                if file in self.arquivos:
                    print file
                    arquivo = codecs.open(os.path.join(root, file), 'r')  # , encoding='latin-1')
                    self.input_lenght += int(commands.getstatusoutput('cat ' + os.path.join(root, file) + ' |wc -l ')[1])
                    print 'Arquivo de entrada possui {} linhas de informacao'.format(int(self.input_lenght) - 1)
                    df_auxiliar.append(pd.read_csv(arquivo, sep=';', low_memory=False, encoding='cp1252'))
                    #df_auxiliar = pd.read_csv(arquivo, sep=';', low_memory=False, encoding='latin-1')
                    #df_auxiliar = pd.read_csv(arquivo, sep=';', nrows=1000, chunksize=500, encoding='latin-1', low_memory=False)
                    #df_enade = pd.read_csv(arquivo, sep=';', low_memory=False)
                    #df_enade = df_enade.loc[:, self.colunas]
        #import pdb;pdb.set_trace()  #para testar o código
        df_programas = pd.concat(df_auxiliar)
        #----------- RENOMEAR NM_ENTIDADE_ENSINO DA FIOCRUZ PARA FUNDACAO OSWALDO CRUZ (FIOCRUZ)  ----------------
        df_programas.replace('FUNDACAO OSWALDO CRUZ', 'FUNDACAO OSWALDO CRUZ (FIOCRUZ)', inplace=True)
        # -------- ADICIONANDO OS CAMPOS AO DF_DISCENTES PARA FAZER O MERGE COM PROGRAMAS E COM CADASTRO DE IES -------------
        df_programas['SG_ENTIDADE_ENSINO_Capes'] = df_programas['SG_ENTIDADE_ENSINO']
        df_programas['NM_ENTIDADE_ENSINO_Capes'] = df_programas['NM_ENTIDADE_ENSINO']
        # drop de algumas colunas de programas que geram duplicidade com cadastro de instituicoes
        df_programas = df_programas.drop(['DS_DEPENDENCIA_ADMINISTRATIVA','CS_STATUS_JURIDICO'], axis=1)

        return df_programas # retorna um (pandas.io.parsers.TextFileReader)

    def pega_arquivo_cadastro_ies_capes(self):
        """
        Este método itera os arquivos de cadastro da CAPES IES em: BASE_PATH_DATA + 'capes/programas/cadastro_instituicoes/'
        que será agregado ao programas e elimina as colunas e linhas vazias.

        PARAMETRO:
            Não recebe parâmetro.

        RETORNO:
            Retorna o df_cad que é o dataframe de cadastro da IES Capes.

        """

        var = '/var/tmp/solr_front/collections/capes/programas/cadastro_instituicoes/'
        for root, dirs, files in os.walk(var):
            for file in files:
                arquivo = codecs.open(os.path.join(root, file), 'r')  # , encoding='latin-1')
                df_cad_temp = pd.read_csv(arquivo, sep=';', low_memory=False, encoding='latin-1')
        # eliminando as colunas vazias do csv.
        df_cadastro_ies = df_cad_temp.dropna(how = 'all', axis = 'columns')
        df_cadastro_ies = df_cadastro_ies.dropna(how = 'all', axis = 'rows')
        # ----- DELETANDO O AN_BASE E DS_DEPENDENCIA_ADMINISTRATIVA PARA NÃO GERAR DUAS COLUNAS IGUAIS APÓS O MERGE ------
        df_cadastro_ies = df_cadastro_ies.drop(['AN_BASE'], axis=1)

        # df_duplic = df_cad.duplicated(['NM_ENTIDADE_ENSINO_Capes'])
        # df_true = 0
        # if df_duplic == True:
        #     df_true = df_duplic
        #import pdb; pdb.set_trace()
        return df_cadastro_ies

    def merge_programas(self, df):
        """
        Este método recebe um dataframe como parâmetro e faz o merge dele com
        o atributo self.ies, que recebe o método pega_arquivo_cadastro_ies_capes,
        passando como chave o campo SG_ENTIDE_ENSINO_Capes.

        PARAMETRO:
            Recebe um dataframe como parâmetro, que o retorno do método pega_arquivo_nome.

        RETORNO:
            Retorna o dataframe com todas as linhas e colunas agregadas.

        """
        print 'Fazendo o merge......'
        #df_merged = df.merge(self.ies, how='left')
        df_merged = df.merge(self.ies, on=['SG_ENTIDADE_ENSINO_Capes', 'NM_ENTIDADE_ENSINO_Capes'])
        #df_merged = df.merge(self.ies, how='left')
        #df_merge = df_merged.loc(colunas_adicionadas)
        #return df_merged[colunas_adicionadas]
        #import pdb; pdb.set_trace()
        return df_merged


    def resolve_dicionarios(self):
        """
        Método para modificar/alterar/atualizar/remover colunas e linhas
        do dataframe e também resolver o(s) dicionário(s), pega o retorno
        do método pega_arquivo_nome, o passa como parâmetro para o
        método merge_programas, substitui os espaços em branco das colunas
        do dataframe por underline, corrige o formato das datas,
        resolve os campos para facet, busca e nuvem de palavras e faz os ajustes
        dos campos do dataframe.

        PARAMETRO:
            Não recebe parâmetro.

        RETORNO:
            Retorna um dataframe pronto para ser convertido em csv pelo método gera_csv.

        """
        df = self.pega_arquivo_nome()
        df['SG_ENTIDADE_ENSINO_Capes'] = df['SG_ENTIDADE_ENSINO']
        df['NM_ENTIDADE_ENSINO_Capes'] = df['NM_ENTIDADE_ENSINO']
        #import pdb; pdb.set_trace()
        df = self.merge_programas(df)
        df.columns = df.columns.str.replace(' ', '_')

        parse_dates = ['DT_SITUACAO_PROGRAMA']

        for dt in parse_dates:
            df[dt] = pd.to_datetime(df[dt], infer_datetime_format=False, format='%d%b%Y:%H:%M:%S', errors='coerce')

        # df['ANO_MATRICULA_facet'] = df[df['DT_MATRICULA'].notnull()]['DT_MATRICULA'].dt.year.apply(gYear)
        #df['DT_SITUACAO_PROGRAMA'] = df[df['DT_SITUACAO_PROGRAMA'].dt.year == '2013']['DT_SITUACAO_PROGRAMA'].dt.year.apply(gYear)
        df['AN_BASE_facet'] = df['AN_BASE'].apply(gYear)
        df['NM_REGIAO_facet'] = df['NM_REGIAO'] + '|' + df['SG_UF_PROGRAMA'] + '|' + df['NM_MUNICIPIO_PROGRAMA_IES']
        df['AREA_CONHECIMENTO_facet'] = df['NM_GRANDE_AREA_CONHECIMENTO'] + '|' + df['NM_AREA_CONHECIMENTO'] + '|' + df['NM_SUBAREA_CONHECIMENTO']
        df['ANO_INICIO_PROGRAMA_facet'] = df['ANO_INICIO_PROGRAMA'].apply(gYear)
        df['AN_INICIO_CURSO_facet'] = df['AN_INICIO_CURSO'].apply(gYear)

        df['DT_SITUACAO_PROGRAMA'] = df[dt].dt.strftime('%Y%m%d')
        df['DT_SITUACAO_PROGRAMA'] = df['DT_SITUACAO_PROGRAMA'].astype(str)
        df['DT_SITUACAO_PROGRAMA_facet'] = df['DT_SITUACAO_PROGRAMA'].apply(data_facet)
        df['INSTITUICAO_ENSINO_facet'] =  df['SG_ENTIDADE_ENSINO'] + '|' + df['NM_ENTIDADE_ENSINO']

        # Campos setados do cadastro CAPES IES
        df['cat_insti'] = df['Tipo_de_Instituicao']
        df['CS_Natureza_Juridica'] = df['Nome_Natureza_Juridica-GEI']
        df['NM_INST_FapespGei'] = df['NM_INST_Gei']
        df['DS_ORGANIZACAO_ACADEMICA_Fapesp'] = df['DS_ORGANIZACAO_ACADEMICA-GEI']

        # CAMPOS PARA BUSCA AVANÇADA
        df['NM_PROGRAMA_IES_exact'] = df['NM_PROGRAMA_IES']
        df['ID_PESSOA_exact'] = df['ID_PESSOA'].astype(str)

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
    passa os parâmetros - arquivo e nome_arquivo para a classe CapesProgramas.

    PARAMETRO:
        Não recebe parâmetro.

    RETORNO:
        Função sem retorno.

    """

    PATH_ORIGEM = '/var/tmp/solr_front/collections/capes/programas/download'
    try:
        arquivos = os.listdir(PATH_ORIGEM)
        arquivos.sort()
        # tamanho_arquivo = len(arquivos) - 1
        # arquivo_inicial = arquivos[0].split('.')[0]
        # arquivo_final = arquivos[tamanho_arquivo].split('.')[0]
        # nome_arquivo = arquivo_inicial +'_a_'+ arquivo_final
        for arquivo in arquivos:
            nome_arquivo = arquivo.split('.')[0]
            capes_doc = CapesProgramas(arquivo, nome_arquivo)
            capes_doc.gera_csv()
        print('Arquivo {} finalizado!'.format(arquivo))

    except OSError:
        print('Nenhum arquivo encontrado')
        raise
