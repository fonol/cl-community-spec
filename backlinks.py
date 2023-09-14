"""
    Regenerate the "backlinks" section on each page.
    Needs beautifulsoup, e.g. `pip install beautifulsoup4`
    Slow, will take ~3-5mins!
"""

import os
import re
import json
import functools
import collections
from bs4 import BeautifulSoup

def get_html_files():
    return [f for f in os.listdir(src_folder_path()) if re.match(r'^.*\.html$', f)]

def folder_path():
    return os.path.dirname(os.path.realpath(__file__))

def src_folder_path():
    return os.path.join(folder_path(), "pages/")


def hneedle(t):
    return t.name in ['h3', 'h4', 'h2', 'h1'] and t.find_parent('div', class_="section top-most")

def bneedle(t):
    if t.name == 'div' and 'section' in t.get('class', []):
        h3 = t.find('h3')
        if h3 and h3.text == 'Backlinks':
            return True
    return False


def run():
    files          = get_html_files()
    file_names     = [f[:-5] for f in files]

    bl             = {}

    flen           = len(files)

    for ix, f in enumerate(files):
        if (ix +1) % 10 == 0:
            print(f"Collecting links ... [{ix+1}/{flen}]")
        if f in ["index.html", "Glossary.html", "unknown_node.html", "setf-classname.html"]:
            continue
        fpath           = os.path.join(src_folder_path(), f)

        # this will be used in the link text
        title           = None

        with open(fpath, 'r') as r:

            html        = r.read()

            soup = BeautifulSoup(html, 'html.parser')

            header = soup.find(hneedle)
            if header.string is None:
                title = re.sub("</?[bi]>", "", str(header.encode_contents())).strip()
            else:
                title = header.string.strip()
            assert(title is not None)
            title = title.replace("\n", " ").replace("  ", " ")

            backlinks = soup.find(bneedle)
            # remove backlinks and nav to not find any anchors from these
            if backlinks:
                backlinks.decompose()
            nav = soup.find("div", {"class":"nav"})
            if nav:
                nav.decompose()


            body_main = soup.find("div", { "class": "body__main__inner"})
            if body_main is None:
                print(fpath)
                continue

            
            anchors = body_main.find_all('a', href=True)
            anchors = [(a.string, a['href']) for a in anchors]
            for txt, href in anchors:
                if "#" in href:
                    href = href[:href.index('#')]
                bl.setdefault(href, [])
                bl[href].append((f, title))


    for ix, f in enumerate(files):
        if (ix +1) % 10 == 0:
            print(f"Inserting links ... [{ix+1}/{flen}]")

        if f == "index.html" or f == "Glossary.html":
            continue

        fpath           = os.path.join(src_folder_path(), f)

        if f not in bl:
            continue
        bls             = bl[f]
        if bls == []:
            continue

        html = ""
        with open(fpath, 'r') as r:

            html        = r.read()
            soup = BeautifulSoup(html, 'html.parser')


            bl_list = [f"<a href=\"{b[0]}\">{b[1]}</a>, " for b in set(bls) if b[0] != f]
            bl_list = "".join(sorted(bl_list, key = lambda b: b[b.index(">"):].lower()))
            bl_list = bl_list[:-2]
            
            blsection = soup.find(bneedle)

            blhtml =  BeautifulSoup(f"""<h3>Backlinks</h3> 
                    {bl_list} """, "html.parser")
            if blsection is None:
                new_section = soup.new_tag("div", **{"class": "section"})
                new_section.append(blhtml)
                body_main = soup.find("div", { "class": "body__main__inner"})
                body_main.append(new_section)
            else:
                blsection.clear()
                blsection.append(blhtml)

            html = str(soup)
        with open(fpath, "w") as o:
            o.write(html)


run()               
 