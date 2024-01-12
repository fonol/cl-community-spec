"""
    Script that was used to create tables from some indented sections in the initial HTML output.
    You most likely do not want to use this anymore.    
"""
import os
import re

def get_html_files():
    files = [f for f in os.listdir(src_folder_path()) if re.match(r'^.*\.html$', f)]
    return files

def folder_path():
    return os.path.dirname(os.path.realpath(__file__))

def src_folder_path():
    return os.path.join(folder_path(), "html_in/")


def create_tables():
    files               = get_html_files()
    found               = []
    for f in files:
        fpath       = os.path.join(src_folder_path(), f)
        has_change  = False

        with open(fpath, 'r') as r:

            content         = r.read()
            out             = []
            lines           = content.splitlines()
            inside          = False
            max_cols        = -1
            for ix, l in enumerate(lines):
                if not inside and l.startswith("<p>&nbsp;&nbsp;<a ") and lines[ix+1].startswith("&nbsp;&nbsp;"):
                    found.append(f)
                    inside = True
                    has_change = True
                    l = re.sub("^<p>&nbsp;&nbsp;<a ", "<table>\n\t<tr><td><a ", l)
                    l = re.sub("(&nbsp;){2,} ?$", "</td></tr>", l)
                    l = re.sub("(&nbsp;){2,}", "</td><td>", l)
                    max_cols = l.count("</td>")
                    out.append(l)
                elif inside and l.startswith("&nbsp;&nbsp;"):

                    l = re.sub("^(&nbsp;){2,}", "\t<tr><td>", l)
                    l = re.sub("(&nbsp;){2,} ?$", "</td></tr>", l)
                    l = re.sub("(&nbsp;){2,}", "</td><td>", l)
                    while l.count("</td>") < max_cols:
                        l = re.sub("</td></tr>", "</td><td></td></tr>", l)
                    assert(l.count("<td>") == l.count("</td>"))
                    out.append(l)
                elif inside and l == "</p>":
                    inside = False
                    out.append("</table>")
                else:
                    inside = False
                    out.append(l)

        if has_change:
            with open(fpath, "w", encoding="utf-8") as outf:
                outf.write("\n".join(out))
    print(f"Created tables in {len(found)} files.")
    print(f"Files:")
    print(found)

create_tables()