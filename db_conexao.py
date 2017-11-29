import psycopg2
import psycopg2.extras
from datetime import datetime


class Conexao(object):
    _db = None

    def __init__(self, mhost=None, db=None, usr=None, pwd=None):
        conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (mhost,db, usr,pwd)
        self._db = psycopg2.connect(conn_string)

    def manipular(self, sql):
        try:
            cur = self._db.cursor()
            cur.execute(sql)
            cur.close()
            self._db.commit()

        except (Exception, psycopg2.DatabaseError) as erro:
            return erro

        return True
		

    def atualizar(self, sql):

        try:

            cur = self._db.cursor()
            cur.execute(u'%s' %(sql))
            cur.close()
            self._db.commit()

        except (Exception, psycopg2.DatabaseError) as erro:
            return erro
        return True


    def proximaPK(self, tabela, chave):
        sql = 'select max(' + chave + ') from ' + tabela
        rs = self.consultar(sql)
        pk = rs[0][0]
        return pk + 1


    def fechar(self):
        self._db.close()
