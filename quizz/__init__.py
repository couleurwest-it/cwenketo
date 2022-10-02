# -*- coding utf-8 -*-
""""Road mapping

home (/) : Accueil "Mes projets en cours et mes alertes
Fiche projet (/about) : Equipe projet, extern actifs, action en cours/en attente / alerte
La structure (/project) : information structure, fonctionnement générale / praticien/ Services...
Suivi : Réunion/rencontre, Compte rendu / Formation (organisation, monitoring)
Déploiement: planning

L'accès n'est autorisé qu'au membre du GCS
Dépot de fihisr sur le cloud (webdav)
"""

import os
import random

import flask
from dreamtools import profiler, tools, dtemng, config as cfg
from flask import flash, url_for
from flask import request, redirect, Flask
from flask_login import login_user, LoginManager, login_required, logout_user
from flask_wtf import CSRFProtect

from quizz.ctrl.constantes import CDirectories, CONSTANTES, CQuizz
from quizz.ctrl.jarvis import CJarvis

os.environ['TZ'] = 'America/Cayenne'  # set new timezone
csrf = CSRFProtect()
login_manager = LoginManager()


def flash_message(code):
    """Gestion des messages flash

    :param str code: code du message
        ERR_FORM : Erreur Formulaire / données non valide
    """

    if code == 'ERR_FORM':
        return flash('<h3>Formulaire non valide<br/><small>Vérifier saisie</small></h3>', "warning")
    elif code == "ACTION_SUCCESS":
        return flash('<h3>Opération effectuée avec succès</h3>', "success")
    elif code == "REC_OK":
        return flash('<h3>Enregistrement effectué</h3>', "success")
    elif code == "ERR_SYS":
        return flash(
            "<h3>Erreur serveur<br/><small>Raffraichir la page et réintérer l'operation<br/>Si l'erreur persiste contactez votre administrateur",
            "error")
    elif code == 'USER_NOT_FIND':
        return flash(
            "<h3>Action impossible<br/><small>Nous n'arrivons pas à vous identifier<br/>Si selon vous il s'agit du'une erreur,persiste contactez votre administrateur",
            "error")
    else:
        return flash(f'<h3>Erreur<br/><small>{code}</small></h3>', "warning")

from flask_simple_captcha import CAPTCHA
captcha = CAPTCHA({'SECRET_CAPTCHA_KEY' : os.getenv('SECRET_CAPTCHA_KEY')})

def create_app():
    action = '[config] Initialisation systemes'
    print(f"---- {action}----")

    app = Flask(__name__)
    app.config.from_object('config.CConfig')

    csrf.init_app(app)
    captcha.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"

    cfg.CConfig("quizz", "development")
    CONSTANTES.DIRECTORIES = CDirectories(tools.PROJECT_DIR)
    CONSTANTES.MASTER_PWD = os.getenv("SUPERPASS")
    app.static_folder = profiler.path_build(tools.PROJECT_DIR, 'static')

    CJarvis.info_tracking("Initialisation filtres Jinja", "[pm] CREATE_APP")

    from quizz.mdl import DBRouter
    DBRouter.DB_SERVER = os.getenv("DB_SERVER")
    DBRouter.PREFIX_DB = os.getenv("PREFIX_DB") or ''

    CQuizz.FILENAME = profiler.path_build(tools.PROJECT_DIR, 'static/sources/question.yml')
    CQuizz.load_questions()

    @login_manager.user_loader
    def load_user(uuid):
        from quizz.mdl.user import DBUser
        user = DBUser.load_document(uuid)

        return user

    @app.template_global('today')
    def today():
        return dtemng.today('%Y-%m-%d')

    @app.template_global('citation')
    def citation():
        textes = ["""Je n'ai fait que te rappeler ce que tu savais déjà.""",
                  """Il faut laisser le passé derrière soi si on veut avancer""",
                  """Parfois, les choses simples sont les plus difficiles à réaliser""",
                  """ Il n’y a pas de vent favorable pour celui qui ne sait pas où il va""",
                  """Le futur a été créé pour être changé""",
                  """Prévoir consiste à projeter dans l’avenir ce qu’on a perçu dans le passé""",
                  """Pour réussir il ne suffit pas de prévoir, il faut aussi savoir improviser""",
                  """Mieux vaut penser le changement que changer le pansement.""",
                  """C'est le désir qui crée le désirable, et le projet qui pose la fin""",
                  """Le numérique est inéluctable, le nier est faire preuve de mauvaise foi""",
                  """Les problème résident dans l'inaction""",
                  """S C'est le désir qui crée le désirable, et le projet qui pose la fin""",
                  """Cherche un arbre et laisse lui t'apprendre le calme.""",
                  """S' il y a problème, il y a solution, s' il y a pas solution, il y a pas problème.""",
                  """Les faibles ont de problèmes. Les forts ont des solutions.""",
                  """Il n'y aurait rien de pire à mes yeux que de participer à un projet préconçu, prémâché, formaté.""",
                  """Se réunir est un début, rester ensemble est un progrès, travailler ensemble est la réussite.""",
                  """Il y a plus d'idées dans deux têtes que dans une.""",
                  """La logique vous conduira d’un point A à un point B. L'imagination et l'audace vous conduiront où vous le désirez. """,
                  """Seuls ceux qui prennent le risque d'échouer spectaculairement réussiront brillamment.""",
                  """ Certains veulent que ça arrive, d'autres aimeraient que ça arrive et quelques-uns fonts que ça arrive. """,
                  """ Le succès est la capacité d'aller d'échec en échec sans perdre son enthousiasme. """,
                  """Aucun de nous n'est autant intelligent que nous tous.""",
                  """Si vous voulez vous élever, soulèvez quelqu'un d'autre.""",
                  """Cela prend deux silex pour faire un feu.""",
                  """Dans le travail d'équipe, le silence n'est pas d'or, c’est mortel.""",
                  """Le seul endroit où le succès vient avant le travail est dans le dictionnaire.""",
                  """La façon de commencer est d'arrêter de parler et de commencer à faire.""",
                  """Même si vous êtes sur la bonne voie, vous vous ferez écraser si vous restez assis là."""]

        return random.choice(textes)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect('/')

    from .roads.quizz import bp
    CJarvis.info_tracking("Configuration des routes", "[pm] CREATE_APP")
    app.register_blueprint(bp)

    @app.route('/', methods=['GET', 'POST'])
    @login_required
    def index():
        start = request.args.get('start', '1')
        end = request.args.get('end', '0')

        return flask.render_template('index.html', start=start, end=end, page="index")

    @app.route('/login', methods=['GET'])
    def login():
        from quizz.mdl.user import DBUser

        email = request.args.get("email")
        if email:
            c_hash = request.args.get('captcha-hash')
            c_text = request.args.get('captcha-text')

            if not captcha.verify(c_text, c_hash):
                flask.flash('Erreur CAPTCHA')
                cp = captcha.create()

                return flask.render_template('login.html', page="login", captcha=cp)

            user = DBUser.find_documents({"email": email})
            if user:
                user = user.pop()
            else:
                uuid = DBUser.insert_one_document(email=email, reponse={})
                user = DBUser.load_document(uuid)

            # Récupération les réponses (les question deja répondu du l'utilisateur)

            login_user(user)

            flask.flash('Logged in successfully.')

            if user.get('reponse'):
                return flask.redirect(url_for('quizz.question'))
            else:
                return flask.redirect(url_for('index', start=1, end=0))

        cp = captcha.create()
        return flask.render_template('login.html', page="login", captcha=cp)

    from .roads.quizz import bp
    app.register_blueprint(bp, name="quizz")

    from .roads import api
    app.register_blueprint(api, name="api")


    return app
