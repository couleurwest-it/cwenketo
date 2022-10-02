# -*- coding: utf-8 -*-
import os
import subprocess

import matplotlib
import numpy as np
from PIL import Image
from dreamtools import profiler
from wordcloud import WordCloud

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from quizz import CONSTANTES
from quizz.ctrl.constantes import CSynthez


class ExtractSynthese:
    MAX_WORDS = 50
    img_src = profiler.path_build(CONSTANTES.DIRECTORIES.pics, 'cloud.png')
    mask = None
    tempath: str = profiler.path_build(CONSTANTES.DIRECTORIES.registar, f'tmp')

    @classmethod
    def do_clouds(cls, cat, text):
        fn = f'{cat}_cloud.png'
        cloud = WordCloud(background_color='#FFFFFF', stopwords=CSynthez.WEXCLUDED,
                          max_words=50, max_font_size=40, random_state=42, mask=cls.mask).generate(text)

        img_dst = profiler.path_build(cls.tempath, fn)
        image = cloud.to_image()
        image.save(img_dst)

        return fn

    @classmethod
    def do_plot(cls, cat, note, evl):
        fn = f'{cat}_note.png'

        img_dst = profiler.path_build(cls.tempath, fn)
        percent = note * 10
        color = CSynthez.COLORS[evl]

        fig, ax = plt.subplots(figsize=(6, 6))

        wedgeprops = {'width': 0.3, 'edgecolor': '#999baa', 'linewidth': 3}
        ax.pie([percent, 100 - percent], wedgeprops=wedgeprops, startangle=270, colors=[color, '#99a5bc'])
        plt.title(cat, fontsize=24, loc='left')
        plt.text(0, 0, f"{note}/10", ha='center', va='center', fontsize=42)
        plt.savefig(img_dst)
        return fn

    @classmethod
    def synthetize(cls, resultats):
        cls.mask = np.array(Image.open(cls.img_src))
        cls.mask[cls.mask == 1] = 255

        profiler.makedirs(cls.tempath)

        cloudword = resultats.get("commentaires")
        rows = []

        for cat, dataset in cloudword.items():
            text = ' '.join(dataset)
            note = resultats['resultats'][cat]["note"]

            if not dataset:
                text = "Personne ne s'est exprimé"

            pic_cloud = cls.do_clouds(cat, text)
            pic_note = cls.do_plot(cat, note, resultats['resultats'][cat]["eval"])

            com = resultats['commentaires'][cat] or 'Aucun commentaires'
            com = list(map(lambda s: rf"\item {s}", com))

            commentaire = CSynthez.LATEX_COM.format(item='\n'.join(com))
            rows.append(CSynthez.LATEX_ROW.format(note=note, pic_note=pic_note, pic_cloud=pic_cloud,
                                                  commentaires=commentaire, categorie=cat))

        row = '\n\\vspace{1cm}\n'.join(rows)

        document = CSynthez.LATEX.format(row=row, pathpics=cls.tempath)

        fname = "resultats"
        tex = profiler.path_build(cls.tempath, f"{fname}.tex")

        with open(tex, 'w', encoding="utf-8") as f:
            f.write(document)

        proc = subprocess.Popen(['pdflatex', "-output-directory", cls.tempath, tex])
        proc.communicate()


        for root, dirs, files in os.walk(cls.tempath):
            for filename in files:

                if filename != f"{fname}.pdf":
                    os.unlink( profiler.path_build(cls.tempath, filename))

        fname = profiler.path_build(cls.tempath, f"{fname}.pdf")
        return fname
