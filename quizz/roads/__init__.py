from flask import Blueprint
from flask_login import login_required

api = Blueprint('api', __name__, url_prefix="/api")


@api.route('suprimonza')
@login_required
def suprimonza():
    from quizz.mdl.user import DBUser
    DBUser.delete_db()
    from quizz.mdl.questions import DBQuestion
    DBQuestion.delete_db()

    return "OK Babe"
