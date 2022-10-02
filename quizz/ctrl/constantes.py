import dataclasses

from dreamtools import cfgmng, profiler

from quizz.mdl.questions import DBQuestion

@dataclasses.dataclass
class CDirectories:
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
    DIRECTORIES: CDirectories
    MASTER_PWD: str

class CSynthez:
    LATEX = r"""\documentclass{{article}}
\usepackage[legalpaper, portrait, margin=0.3in]{{geometry}}
\usepackage{{graphicx}}  

\title{{Synthèse enquête de satisfaction}}
\author{{Formation HM - Eté 2022}}
\date{{\today}}

\graphicspath{{{pathpics}}}
\begin{{document}}
\sffamily  
\maketitle
{row} 
\end{{document}}"""
    LATEX_ROW = r"""\section*{{\large{{{categorie} : Note {note}/10}}}}
\begin{{minipage}}{{0.3\linewidth}}
    \centering
    \includegraphics[width=\linewidth]{{{pic_note}}}
\end{{minipage}}
\begin{{minipage}}{{0.60\linewidth}}
    \centering
    \includegraphics[width=\linewidth]{{{pic_cloud}}}
\end{{minipage}}
\vspace{{10pt}}
\subsection*{{Commentaires}}
{commentaires}"""
    LATEX_COM = r""" \begin{{itemize}}
{item}
\end{{itemize}}"""
    COLORS = ["#a50000", "#a50000", "#f93e9b", "#bb00bb", "#63287a", "#37029a", "#047295", "#01cbd1", "#24b881",
              "#6bf904", "#f5ff00"]
    WEXCLUDED = {
        'd', 'du', 'de', 'la', 'des', 'le', 'et', 'est', 'elle', 'une', 'en', 'que', 'aux', 'qui', 'ces',
        'les', 'dans', 'sur', 'l', 'un', 'pour', 'par', 'il', 'ou', 'à', 'ce', 'a', 'sont', 'cas', 'plus',
        'leur', 'se', 's', 'vous', 'au', 'c', 'aussi', 'toutes', 'autre', 'comme', "c'est", 'je', 'tu', 'il', 'nous',
        'vous',
        'ils', 'on', 'est'}

