#
# encoding: utf-8
# Prog para correrção da Rejeição 629: Valor do Produto difere do produto Valor Unitário de Comercialização e Quantidade Comercial
# Autor: Filipe Rocha
# Data: 14/10/2017
# Versão: 1.0

import os
import sys
from time import *
from datetime import datetime
from db_conexao import Conexao


_db_name, db_host, _db_user, _db_pwd = '','','',''
_txt_config = 'config.txt'

#Conig padrao de acesso ao banco de dados
txt_param = 'path=localhost\n banco=autosystem\n user=postgres\n password=postgres'

#Verificação se existe a configuração  de acesso ao banco de dados e se não exisitr ele cria a configuração padrao
if not os.path.exists(_txt_config):
    txt_config = open(_txt_config, 'w')
    txt_config.write('%s' % (txt_param.replace(' ','')))
    txt_config.close()

if os.path.exists(_txt_config):
    _db_config = open('config.txt','r')
    _conteudo  = _db_config.readlines()

    for row in _conteudo:
        config = row.split('=')
        if config[0] == 'path':
            _db_host = config[1].rstrip('\n')
        if config[0] == 'banco':
            _db_name = config[1].rstrip('\n')
        if config[0] == 'user':
            _db_user = config[1].rstrip('\n')
        if config[0] == 'password':
            _db_pwd = config[1].rstrip('\n')

    _db_config.close()
    conn = Conexao(_db_host,_db_name,_db_user,_db_pwd)

#Gera o log dos sql executados no banco de dados.
def logg(str):
    caminho = 'log'
    arquivo = caminho + '/log.txt'
    now = datetime.now()

    if not os.path.exists(caminho):
        os.makedirs(caminho)
    if not os.path.exists(arquivo):
        open(arquivo, 'w')
    else:
        srt_log = open(arquivo,'a')
        srt_log.writelines("\n%s = %s " %(now, str.replace('  ',' ')))
        srt_log.close()

#Percorre os items da NF-e a procura de valores divergentes
def verifica_valor_divergente(codigo, modelo_doc, nr_nota):

    empresa = None
    rs_empresa = conn.consultar("select grid from empresa where codigo='%s'" % (codigo))
    for rs in rs_empresa:
        empresa = rs[0]
        if empresa is not None:
                sql = """ SELECT nfp.grid, nfp.quantidade as qtd, nfp.preco_unit, nfp.valor_desconto as desconto, nfp.valor_acrescimo as acrescimo, ROUND(CAST(nfp.quantidade * nfp.preco_unit AS NUMERIC),2) AS valor_sefaz, nfp.valor AS valor_autosystem, nfp.subtotal, CASE WHEN  ROUND(CAST(( nfp.valor - (nfp.quantidade * nfp.preco_unit)) AS NUMERIC),2) >= 0.02 OR  ROUND(CAST(( nfp.valor - (nfp.quantidade * nfp.preco_unit)) AS NUMERIC),2) <= -0.02 THEN 'SIM' ELSE 'NAO' END AS diff, ROUND(CAST(( nfp.valor - (nfp.quantidade * nfp.preco_unit)) AS NUMERIC),2) as valor_diff FROM nota_fiscal_produto nfp JOIN nota_fiscal nf ON(nfp.nota_fiscal=nf.grid) WHERE nf.empresa='%s' and nf.modelo='%s' and nf.numero_nota='%s'""" %(empresa, modelo_doc, nr_nota)

                result = conn.consultar(sql)
                logg(sql)
                return  result

        else:
            return False

#Separa apenas os registros que precisa ser corrigidos.
def verifica_produto_atualizar(item):
    atualiza = []
    for produto in item:
        if produto[8] == 'SIM':
            atualiza.append(produto)
    return atualiza

#Função principal
def main():

    def menu():
        print (" +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print (" |         Scritp para correcao da Rejeicao 629            |")
        print (" +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print (" |                        MENU                             |")
        print (" +---------------------------------------------------------+")
        print (" | 1 - Visualizar regisgros com divergencia                |")
        print (" | 2 - Realizar correcao QTD x PRECO UNIT                  |")
        print (" | 0 - Sair                                                |")
        print (" +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    print "\n INICIANDO PROG..."
    op = '1'
    while op !='0':
        os.system('cls')
        menu()
        op = raw_input(" Opacao: ")

        if op == '1':
            cod_empresa = input("\n Codigo Empresa: ")
            modelo      = input("    Modelo NF-e: ")
            numero_nota = input("    Numero Nota: ")
            item = verifica_valor_divergente(cod_empresa,modelo, numero_nota)

            if item is None:
                print "\n ### Empresa nao localizada... ### \n"
                os.system("PAUSE")
            else:
                list = verifica_produto_atualizar(item)
                if len(list) > 0:
                    os.system("cls")
                    print (" +========================== DIVERGENCIAS ENCONTRADAS ===============================+ ")
                    print (" | Grid      | Quantidade   | Preco Unit  | Valor Sefaz   | Valor ATS   | Diferencao |")
                    print (" +-----------+--------------+-------------+---------------+-------------+------------+")

                    for row in list:
                        print " | {0}    | {1}        | {2}\t  | {3}\t  | {4}\t| {5}\t     |".format(row[0], row[1],row[2], row[5],row[6], row[9])

                    print("\n")
                    os.system("PAUSE")

                else:
                    print "\n ### NF-e nao localizada ou nao possui divergencia a ser corrigidas... ###\n"
                    os.system("PAUSE")

        if op =='2':
            cod_empresa = input("\n Codigo Empresa: ")
            modelo      = input("      Modelo NF-e: ")
            numero_nota = input("      Numero Nota: ")
            item = verifica_valor_divergente(cod_empresa, modelo, numero_nota)

            if item is None:
                print "\n ### Empresa nao localizada ###\n"
                os.system("PAUSE")
            else:
                list = verifica_produto_atualizar(item)
                if len(list) > 0:
                    print "\n ### Preparando registros para correcao... ###\n"

                    for row in list:
                        sql = "update nota_fiscal_produto set valor='%.2f', subtotal='%.2f' where grid='%s'" % (row[5],row[5],row[0])
                        rs  = conn.atualizar(sql)
                        print " GRID: {0} - OK".format(row[0])

                    if rs:
                        print("\n ### Registros atualizados com sucesso... ###")
                        os.system("PAUSE")
                    else:
                        print("\n ### Erro ao tentar atualizar registros... ###\n")
                        os.system("PAUSE")
                else:
                    print "\n ### NF-e nao localizada ou nao possui divergencia a ser corrigidas... ###\n"
                    os.system("PAUSE")

        if op == '0':
            print("\n PROG finalizado...")
            break

#Faz a chamada do prog.
if __name__ == '__main__':
    main()
    os.system("PAUSE")

