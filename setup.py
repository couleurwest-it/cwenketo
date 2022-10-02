from setuptools import setup

setup(
    name= "CWEnketo",
    version='1.0.0',
    packages=['quizz'],

    setup_requires=['libsass >= 0.21.0'],
    sass_manifests={'.': ('.sources/stylesheet', 'static/xcss', 'static/css')}

)



"""
Copiright fonts : <div>Font made from <a href="http://www.onlinewebfonts.com">oNline Web Fonts</a>is licensed by CC BY 3.0</div>
 Copyright (c) 2011 by Santiago Orozco (hi@typemade.mx) with reserved name Italiana 
"""