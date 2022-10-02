# -*- coding: utf-8 -*-

import getopt
import os
import subprocess
import sys

import numpy as np
from PIL import Image
from dreamtools import profiler, cfgmng
from matplotlib import pyplot as plt
from wordcloud import WordCloud

path = profiler.dirproject()

img_src = profiler.path_build(path, 'cloud.png')
mask = np.array(Image.open(img_src))
mask[mask == 1] = 255
max_words = 50
exclure_mots = {
    'd', 'du', 'de', 'la', 'des', 'le', 'et', 'est', 'elle', 'une', 'en', 'que', 'aux', 'qui', 'ces',
    'les', 'dans', 'sur', 'l', 'un', 'pour', 'par', 'il', 'ou', 'à', 'ce', 'a', 'sont', 'cas', 'plus',
    'leur', 'se', 's', 'vous', 'au', 'c', 'aussi', 'toutes', 'autre', 'comme', "c'est", 'je', 'tu', 'il', 'nous',
    'vous',
    'ils', 'on', 'est'}

latex = r"""\documentclass{{article}}
\usepackage[legalpaper, portrait, margin=0.3in]{{geometry}}
\usepackage{{graphicx}}  

\title{{Synthèse enquête de satisfaction}}
\author{{Formation HM - Eté 2022}}
\date{{\today}}

\begin{{document}}
\sffamily  
\maketitle
{row} 
\end{{document}}
"""
latex_row = r"""\section*{{\large{{{categorie} : Note {note}/10}}}}
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
{commentaires}
"""
latex_commentaire = r"""
 \begin{{itemize}}
    {item}
\end{{itemize}}"""

COLORS = ["#a50000","#a50000","#f93e9b","#bb00bb","#63287a","#37029a","#047295","#01cbd1","#24b881","#6bf904","#f5ff00"]

def do_clouds(cat, text):
    fn= f'{cat}_cloud.png'
    cloud = WordCloud(background_color='#FFFFFF', stopwords=exclure_mots,
                      max_words=50,max_font_size=40, random_state=42, mask=mask).generate(text)

    img_dst = profiler.path_build(path,fn)
    image = cloud.to_image()
    image.save(img_dst)

    return fn

def do_plot(cat, note, evl):
    fn= f'{cat}_note.png'
    img_dst = profiler.path_build(path, fn)

    percent = note * 10
    color = COLORS[evl]

    fig, ax = plt.subplots(figsize=(6, 6))
    wedgeprops = {'width': 0.3, 'edgecolor': '#999baa', 'linewidth': 3}
    ax.pie([percent, 100 - percent], wedgeprops=wedgeprops, startangle=270, colors=[color, '#99a5bc'])
    plt.title(cat, fontsize=24, loc='left')
    plt.text(0, 0, f"{note}/10", ha='center', va='center', fontsize=42)
    plt.savefig(img_dst)
    return fn

if __name__ == "__main__":
    rst = profiler.path_build(path, "resultat.json")
    rows = []
    if not profiler.file_exists(rst):
        args = sys.argv[1:]
        try:
            opts, args = getopt.getopt(args, "f:", ["file ="])
            if not opts:
                raise ValueError("pas de donner")
        except getopt.GetoptError:
            print("pas de resultat a traiter")
            sys.exit(1)
        except:
            print("pas de resultat a traiter")
            sys.exit(1)

        for opt, arg in opts:
            if opt in ("-f", "--file"):
                rst = arg

    resultats = cfgmng.CFGEngine.loading(rst)
    cloudword = resultats.get("commentaires")

    for cat, dataset in cloudword.items():
        text = ' '.join(dataset)
        note = resultats['resultats'][cat]["note"]

        if not dataset:
            text = "Personne ne s'est exprimé"

        pic_cloud = do_clouds(cat, text)
        pic_note =  do_plot(cat, note, resultats['resultats'][cat]["eval"])

        com = resultats['commentaires'][cat] or 'Aucun commentaires'
        com = list(map(lambda s: rf"\item {s}", com))
        commentaire = latex_commentaire.format(item= '\n'.join(com))

        rows.append(latex_row.format(note=note, pic_note=pic_note, pic_cloud=pic_cloud,
                                        commentaires=commentaire, categorie=cat))


    row = '\n\\vspace{1cm}\n'.join(rows)

    document = latex.format(row=row)

    tex = profiler.path_build(path, "resultats.tex")

    with open(tex, 'w', encoding="utf-8") as f:
        f.write(document)

    proc = subprocess.Popen(['pdflatex', tex])
    proc.communicate()
    os.unlink(tex)
    os.unlink("resultats.log")
