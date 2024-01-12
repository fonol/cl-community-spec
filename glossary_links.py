"""
    Script that was used to turn keywords inside tables or italic/bold text into links to the glossary page. 
    You most likely do not want to use this anymore, if you find some link that is not correct/missing, please change
    it in the HTML in pages/ directly.
"""
import os
import re
from bs4 import BeautifulSoup

def get_html_files():
    files = [f for f in os.listdir(src_folder_path()) if re.match(r'^.*\.html$', f)]
    return files

def folder_path():
    return os.path.dirname(os.path.realpath(__file__))

def src_folder_path():
    return os.path.join(folder_path(), "html_out/")

def get_glossary_terms():

    lines = None
    with open("glossary-terms.txt", "r") as g:
        lines = g.readlines()
        lines = [l.strip() for l in lines if len(l.strip()) > 0]

    return lines

def lookup(term, glossary_terms):

    tc = term.replace("-", "_002d").replace("/", "_002f").replace(" ", "-")
    if tc in glossary_terms:
        return tc

    return None

def cleanup(html):
    soup = BeautifulSoup(html, 'html.parser')

    for card in soup.find_all('div', { 'class': 'section top-most'}):
        if card.find('div', { 'class': 'node-type'}):
            for a in card.find_all('a'):
                a.replace_with(a.string if a.string else '')

    for tag in soup.find_all(['code', 'pre']):
        for a in tag.find_all('a'):
            a.replace_with(a.string if a.string else '')

    for table in soup.find_all('table', {'class': 'arguments-table'}):
        for row in table.find_all('tr'):
            first_td = row.find('td')
            if first_td:
                for a in first_td.find_all('a'):
                    a.replace_with(a.string if a.string else '')

    return str(soup)


def run():
    files               = get_html_files()
    glossary_terms      = set(get_glossary_terms())

    cfound              = 0
    nfound              = set()
    rit                 = re.compile("<i>[^<>]+</i>")
    for f in files:
        fpath       = os.path.join(src_folder_path(), f)
        has_change  = False

        with open(fpath, 'r') as r:

            content          = r.read()

            italic_terms     = set([str(m) for m in re.findall(rit, content)])

            for t in italic_terms:
                term = t[3:-4].replace("&nbsp;", " ").replace("\n", " ")

                id = lookup(term, glossary_terms)
                if id is None and (term.endswith("es") or term.endswith("ed")): 
                    id = lookup(term[:-2], glossary_terms)
                if id is None and term.endswith("s"): 
                    id = lookup(term[:-1], glossary_terms)
                    if id is None and term[0].isupper():
                        id = lookup(term[0].lower() + term[1:-1], glossary_terms)
                if id is None and term[0].isupper():
                    id = lookup(term[0].lower() + term[1:], glossary_terms)

                if id is None:
                    nfound.add(term)
                else:
                    cfound += 1
                    content = re.sub(f"<i>{re.escape(term)}</i>", f"<i><a href=\"Glossary.html#{id}\">{term}</a></i>", content)
                    has_change = True

        if has_change:
            content = cleanup(content)
            with open(fpath, "w", encoding="utf-8") as outf:
                outf.write(content)

    cnfound = len(nfound)

    print(nfound)
    print("---------------------------------------------------")
    print(f"Found the glossary link for {cfound}/{cfound + cnfound} ({int(cfound * 1000 / (cfound + cnfound)) / 10.0}%) <i>...</i> tags.")


run()