# -*- coding: utf-8 -*-

__all__ = ['DBRouter']

import couchdb3
from couchdb3 import Document
from dreamtools import dtemng

action = '[wapp.models.couchdb]'


class DBRouter(Document):
    __dbserve = None

    _dbname = None
    __db = None

    __required__ = None
    __map__ = None
    __server = None
    __indexes__ = []

    __default__ = {}
    __design__ = {}

    PREFIX_DB = ''
    DB_SERVER = ''

    created = dtemng.dtets()
    updated = created

    def __new__(cls, *args, **kwargs):
        with couchdb3.Server(DBRouter.DB_SERVER) as client:
            dbname = cls.dbname()
            if dbname not in client:
                client.create(dbname)
            cls.prepare(client)
        return super(DBRouter, cls).__new__(cls, *args, **kwargs)

    @property
    def db_name(self):
        return f'{DBRouter.PREFIX_DB}{self._dbname}'

    @classmethod
    def dbname(cls):
        return f'{DBRouter.PREFIX_DB}{cls._dbname}'

    @classmethod
    def prepare(cls, client):
        """Initialisation des bases de données, schema et contrainte"""
        # CJarvis.info_tracking(cls._dbname, f'{action} Initialize DB')
        db = client.get(cls.dbname())
        try:
            db.put_design(**cls.__design__)
            for idx in cls.__indexes__:
                db.save_index(**idx)
        except Exception as ex:
            print(ex)

    @classmethod
    def all_document(cls):
        with cls() as db:
            result = None

            dcm = db.all_docs(include_docs=True)
            if dcm.total_rows > 0:
                result = list(map(lambda dc: db.get(dc.id), filter(lambda dc: '_design' not in dc.id, dcm.rows)))

            return result

    @classmethod
    def all_docid(cls):
        with cls() as db:
            dcm = db.all_docs()
            return list(map(lambda dc: dc.id, filter(lambda dc: '_design' not in dc.id, dcm.rows)))

    @classmethod
    def insert_one_document(cls, **dc):
        """Save and return document"""
        with cls() as db:
            dcm = cls().__default__.copy()
            dcm.update(**dc)

            uuid, result, rev = db.create(dcm)

        return uuid

    @classmethod
    def update_one_document(cls, uuid, newDoc):
        """Save and rettur document"""
        result = None

        with cls() as db:
            if uuid in db:
                oldDoc = db.get(uuid)
                oldDoc.update(newDoc)
                db.save(oldDoc)

        return result

    @classmethod
    def find_documents(cls, where, **kwargs):
        """Récupération d'un document
        selector: Dict, limit: int = 25,
         skip: int = 0,
         sort: List[Dict] = None,
         fields: List[str] = None,
         use_index: Union[str, List[str]] = None,
         conflicts: bool = False, r: int = 1,
          bookmark: str = None, update: bool = True,
          stable: bool = None, execution_stats: bool = False
        """
        with cls() as db:
            doc = db.find(where, **kwargs)
            return list(map(lambda dc: cls(**dc), doc['docs']))

    @classmethod
    def delete_one_document(cls, uuid) -> bool:
        """Supression d'un document grace à son id

        :param uuid: identifiant document à supprimer
        :return bool: True or False | None id inexistant
        """
        result = None
        with cls() as db:
            if uuid in db:
                result = db.delete(docid=uuid, rev=db.rev(uuid))

        return result

    @classmethod
    def delete_db(cls):
        with cls() as db:
            dcm = db.all_docs(include_docs=True)
            for row in dcm.rows:
                if row['id'].startswith('_'):
                    continue
                doc = row['doc']
                doc['_deleted'] = True

                db.save (doc)

    @classmethod
    def load_document(cls, uuid) -> Document:
        """Récupération document à partir de son id
        :param uuid: identifiant du document recherché
        :return Document: document
        """
        result = None
        with cls() as db:
            if uuid in db:
                result = cls(db.get(uuid))

        return result

    @classmethod
    def execute_view(cls, ddoc, views, **kwargs):
        """Save and return document"""
        with cls as db:
            return db.view(ddoc, views, **kwargs)

    def __enter__(self):
        self.__server = couchdb3.Server(DBRouter.DB_SERVER)
        return self.__server.get(self.db_name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__server.session.close()
        self.__server = None
