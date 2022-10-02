import dataclasses

from dreamtools import cfgmng, profiler

from quizz.mdl.questions import DBQuestion


class CQuizz:
    PRESENTATION = """Ce questionnaire de satisfaction nous permet de nous améliorer.<br/> Merci pour votre contribution."""
    CATEGORIES = {
        "avis": [(0, "tres insatisfait"), (3, "plutot insatisfait"), (7, "plutot satisfait"), (8, "Très satisfait")],
        "eval": (1, 11)
    }
    FILENAME = "question.yml"
    questions = {}

    @dataclasses.dataclass
    class CQuestion:
        c: str
        t: str  # titre
        q: str  # question
        cq: str = "qcu"
        r: list = None  # question
        uuid: str = None

        def __post_init__(self):
            # Enregistrement des qestion dans la base de donnée
            self.uuid = DBQuestion.insert_one_document(categorie=self.c, title=self.t,
                                                      question=self.q, typeq=self.cq, proposition=self.r)
            pass

    @classmethod
    def load_questions(cls):
        if profiler.file_exists(cls.FILENAME):
            dc = cfgmng.CFGEngine.loading(cls.FILENAME)
            eval = [(x, x) for x in range(cls.CATEGORIES['eval'][0], cls.CATEGORIES['eval'][1])]

            for k, v in dc.items():
                q = cls.questions[k] = []
                for d in v:
                    r = d['r']
                    if r['t'] == 'avis':
                        q.append(cls.CQuestion(k, d['t'], d['q'], r=cls.CATEGORIES['avis']))
                    elif r['t'] == 'eval':
                        q.append(cls.CQuestion(k, d['t'], d['q'], r=eval, cq=r['t']))
                    elif r['t'] == 'choix':
                        q.append(cls.CQuestion(k, d['t'], d['q'], r= [(k, v) for k,v in  r['v'].items()]))
                    else:
                        q.append(cls.CQuestion(k, d['t'], d['q'], cq=r['t']))

            cfgmng.CFGEngine.save_cfg(dc, cls.FILENAME +"_done" )
            profiler.remove_file(cls.FILENAME)
class CONSTANTES:
    DIRECTORIES: str
    MASTER_PWD: str


@dataclasses.dataclass
class Directories:
    projet: str
    app: str  = dataclasses.field(init=False)
    pics: str  = dataclasses.field(init=False)
    registar: str  = dataclasses.field(init=False)
    calendar:  str  = dataclasses.field(init=False)

    def __post_init__(self):
        self.app = profiler.path_build(self.projet, "pm")
        self.pics = profiler.path_build(self.projet, 'static/pics')
        self.registar = profiler.path_build(self.projet, 'static/registar')
        self.calendar = profiler.path_build(self.registar, 'calendar.yml')

        profiler.makedirs(self.registar)