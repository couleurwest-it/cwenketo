# -*- coding: utf-8 -*-

import os.path

import dreamtools
import dreamtools.tools
import rcssmin
import rjsmin
from dreamtools import profiler

"""
This script does 3 things:
    - Minifies css
    - Minifies JavaScript
"""


def minify_css(directory:str, ss_map: list):
    print("Minifying css files: START")
    css_source = profiler.path_build(directory, 'xcss')
    css_dest = profiler.path_build(directory, 'css')

    for source in css_map:
        src = profiler.path_build(css_source, f'{source}.scss.css')
        if not os.path.exists(src):
            src = profiler.path_build(css_source, f'{source}.sass.css')
            if not os.path.exists(src):
                continue

        dst = profiler.path_build(css_dest, f'{source}.min.css')

        with open(src, "r") as infile:
            with open(dst, "w") as outfile:
                outfile.write(rcssmin.cssmin(infile.read()))
        os.remove(src)
    print("Minifying css files: DONE")

def minify_javascript(js_map: list):
    print("Minifying JavaScript files:")

    for source in js_map.items():
        src = f'{source}.scss.css'
        dst = f'{source}.min.css'

        with open(src, "r") as infile:
            with open(dst, "w") as outfile:
                outfile.write(rjsmin.jsmin(infile.read()))

        print(f"{source} minified to {dst}")


if __name__ == "__main__":
    directory = profiler.dirproject()
    directory =  profiler.path_build(directory, 'static')

    js_file = profiler.path_build(directory, 'static/js')

    # Map scss source files to css destination files
    css_map = ['pm', 'scroll', 'radiobutton']

    # Map un-minified JavaScript source files to minified JavaScript destination files
    js_map = []

    print(directory)
    print("Starting runner")
    print("--------------------")
    if css_map:
        minify_css(directory, css_map)
        print("--------------------")
    if js_map:
        minify_css(js_map)
        print("--------------------")
    print("Done")
