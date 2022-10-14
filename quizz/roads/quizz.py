# -*- coding: utf-8 -*-
import json
import math
from copy import copy

import dreamtools.tools
import flask
from flask import Blueprint
from flask_login import current_user, login_required

__all__ = ['question']


from quizz import CONSTANTES

bp = Blueprint('quizzy', __name__, url_prefix="/quizz")


@bp.route('/question', methods=['POST', 'GET'])
@login_required
def question():
    if flask.request.method == "POST":
        form = flask.request.form.to_dict()
        typeq = form.get("typeq")
        if typeq == "words":
            r = list(filter(lambda l: l, [form['reponse-1'], form['reponse-2'], form['reponse-3']]))
            current_user.repondre(form['uuid'], r)
        elif typeq in ['txt', 'qcu', 'eval']:
            current_user.repondre(form['uuid'], form['reponse'])

    from quizz.mdl.questions import DBQuestion

    reponse = current_user.get('reponse', {}).keys()
    question = list(filter(lambda dc: dc.id not in reponse, DBQuestion.all_document()))

    if question:
        return flask.render_template('question.html', dc=question[0], page="index")
    else:
        return flask.redirect(flask.url_for('index', start=0, end=1))


@bp.route('/synthese', methods=['GET', 'POST'])
@login_required
def synthese():
    """
    from wordcloud import WordCloud, STOPWORDS
    import numpy as np
    from PIL import Image
    from mtbpy import mtbpy
    """
    if flask.request.method == "GET":
        return flask.render_template('synthese.html', page="synthese")

    superpass = flask.request.form.get("superpass")
    if superpass != CONSTANTES.MASTER_PWD:
        flask.flash("Saisir un mot de passe valide")
        return flask.render_template('synthese.html', page="shythses")

    from quizz.mdl.questions import DBQuestion
    question = {dc.id: dc.get('categorie') for dc in DBQuestion.all_document()}
    cat_result = DBQuestion.maxResult()

    uuid_categorie = list(cat_result.keys())
    sz = len(uuid_categorie)
    results = dict(zip(uuid_categorie, [0] * sz))
    cloudword = dict(zip(uuid_categorie, [[]] * sz))
    comms = dict(zip(uuid_categorie, [[]] * sz))

    del uuid_categorie

    from quizz.mdl.user import DBUser
    participants = DBUser.all_document()
    nb_participant = len(participants)

    for p in participants:
        for uuid, value in p.get('reponse').items():
            ct = question[uuid]
            if type(value) is list:
                c = copy(cloudword[ct])
                c.append(str(value).lower())
                cloudword[ct] = c
            elif value.isdigit():
                results[ct] += int(value)
            else:
                c = copy(comms[ct])
                c.append(dreamtools.tools.clean_space(value))
                comms[ct] = c

    for cat, vl in cat_result.items():
        note = (results[cat] * 10) / (nb_participant * vl)
        results[cat] = {'eval': math.ceil(note), 'note': round(note, 1)}

    from quizz.ctrl.synthese import ExtractSynthese
    synthese = ExtractSynthese.synthetize({"resultats": results, "commentaires": comms})

    return flask.send_file(synthese, as_attachment=True)