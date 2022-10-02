# -*- coding: utf-8 -*-

from quizz.mdl import DBRouter

views = {
    "maxResult": {
        "map": """function (doc) {
if (doc.typeq == "qcu" || doc.typeq == "eval") {
    var max =  0;
    for (var d in doc.proposition){
      var v =  doc.proposition[d];
      max = Math.max(v[0], max)
    }
    
    emit(doc.categorie, max);
}
}""",
        "reduce": """_sum"""
    }
}


class DBQuestion(DBRouter):
    _dbname = "question"
    _ddoc = f"design{_dbname.capitalize()}"
    categorie: str
    title: str
    question: str
    typeq: str
    proposition: list

    __liste = None
    __default__ = {}
    __design__ = {
        "ddoc": _ddoc,
        "language": "javascript",
        "views": views,
        "validate_doc_update": """function(newDoc, oldDoc, userCtx) {
            function required (field, msg){
                msg = msg | "Données manquante : " + field;
                if (!newDoc[field]) throw ({forbidden: msg}); 
            }
            required ("categorie");
            required("title");
            required("question");

        }""",
    }
    __indexes__ = [
        {
            "ddoc": "index_categorie",
            "index": {
                "fields": ["categorie"]
            },
            "name": "idxcategorie"
        }]

    @staticmethod
    def all_questions():
        if DBQuestion.__liste is None:
            DBQuestion.__liste = DBQuestion.all_document()

        return DBQuestion.__liste

    @classmethod
    def maxResult(cls):
        """Récupération des valeurs max par catégorie"""
        return {dc.key: dc.value for dc in cls.execute_view(cls._ddoc, "maxResult", reduce=True, group_level=1).rows}
