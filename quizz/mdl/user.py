from quizz.mdl import DBRouter

views = {
    "findUser": {
        "map": """function(doc) { emit(doc.email, doc._id)}"""
    }
}


class DBUser(DBRouter):
    _dbname = "user"
    email: str
    reponse: dict = {}

    __default__ = {}
    __design__ = {
        "ddoc": f"design{_dbname.capitalize()}",
        "language": "javascript",
        "views": views,
        "validate_doc_update": """function(newDoc, oldDoc, userCtx) {
            function required (field, msg){
                msg = msg | "Données manquante : " + field;
                if (!newDoc[field]) throw ({forbidden: msg}); 
            }

            if (!oldDoc) 
                required ("email");
                       
        }""",
    }
    __indexes__ = [
        {
            "ddoc": "index_email",
            "index": {
                "fields": ["email"]
            },
            "name": "idxemail"
        }]

    _question: list = []

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    @property
    def question(self):
        return self._question

    @question.setter
    def question(self, v):
        self._question = v

    def repondre(self, uuid, value):
        self['reponse'][uuid] = value
        DBUser.update_one_document(self.id, {"reponse" : self['reponse'] })
        return list(self['reponse'].keys())


