import os
import re
import json


def get_html_files():

    files = [f for f in os.listdir(src_folder_path()) if re.match(r'^.*\.html$', f)]
    return files

def folder_path():
    return os.path.dirname(os.path.realpath(__file__))

def src_folder_path():
    return os.path.join(folder_path(), "html_in/")

def out_folder_path():
    return os.path.join(folder_path(), "output/")


def insert_table_links():
    files               = get_html_files()
    file_names          = [f[:-5] for f in files]

    file_names_re       = "|".join([re.escape(fn) for fn in file_names if len(fn.strip()) > 0 and fn != "list" and fn != "or" and fn != "and"])

    for f in files:
        fpath       = os.path.join(src_folder_path(), f)

        with open(fpath, 'r') as r:

            content        = r.read()
            content        = re.sub(f"(&nbsp;|<b>)(?:<span class=\"nolinebreak\">)?({file_names_re})(?:</span>)?(&nbsp;|</b>)", "\\1<a href=\"\\2.html\">\\2</a>\\3", content)

        with open(fpath, "w", encoding="utf-8") as outf:
            outf.write(content)

def insert_escaped_links():
    files               = get_html_files()
    file_names          = [f[:-5] for f in files if f.startswith("002") or  "_002" in f or "_006" in f]

    file_names          = [(fn.replace("_002d", "-")
                                .replace("_002a", "*")
                                .replace("_002b", "+")
                                .replace("_002f", "/")
                                .replace("_0028", "(")
                                .replace("_0029", ")")
                                .replace("_0060", "`")
                                .replace("_0026", "&")
                                .replace("_0027", "'")
                                , fn) for fn in file_names if len(fn.strip()) > 0]

    for f in files:
        fpath       = os.path.join(src_folder_path(), f)

        with open(fpath, 'r') as r:

            content        = r.read()
            for fprint, flink in file_names:
                if fprint.startswith("002a"):
                    fprint = "*" +fprint[4:]
                elif fprint.startswith("002b"):
                    fprint = "+" +fprint[4:]
                elif fprint.startswith("002d"):
                    fprint = "-" +fprint[4:]
                elif fprint.startswith("002f"):
                    fprint = "/" +fprint[4:]
                elif fprint.startswith("0028"):
                    fprint = "(" +fprint[4:]
                if "002" in fprint or "006" in fprint:
                    print(fprint)
                assert(not "002" in fprint)
                assert(not "006" in fprint)
                content = content.replace(f"&nbsp;&nbsp;{fprint}&nbsp;&nbsp;", f"&nbsp;&nbsp;<a href=\"{flink}.html\">{fprint}</a>&nbsp;&nbsp;")
                content = content.replace(f"&nbsp;<span class=\"nolinebreak\">{fprint}</span>&nbsp;", f"&nbsp;<a href=\"{flink}.html\">{fprint}</a>&nbsp;")
                content = content.replace(f"<b><span class=\"nolinebreak\">{fprint}</span></b>", f"<b><a href=\"{flink}.html\">{fprint}</a></b>")
                content = content.replace(f"<b>{fprint}</b>", f"<a href=\"{flink}.html\">{fprint}</a>")
                


        with open(fpath, "w", encoding="utf-8") as outf:
            outf.write(content)


def main():

    files               = get_html_files()
    nodes               = []

    to_write            = []
    backlinks           = {}
    keys_to_label       = {}

    all_fnames          = [f for f in files]

    for f in files:


        fpath       = os.path.join(src_folder_path(), f)
        outpath     = os.path.join(out_folder_path(), f)


        with open(fpath, 'r') as r:

            all_text        = r.read()
            in_section      = False
            out             = []
            section_cnt     = 0
            in_style        = False
            in_header       = False
            in_table        = False

            n_up            = None
            n_prev          = None
            n_next          = None
            n_next_title    = None
            n_up_title      = None
            n_prev_title    = None

            title           = None

            skip            = 0
            if f == "index.html":
                out = all_text.split("\n")
            else:
                for ix, l in enumerate(all_text.split("\n")):
                    if skip > 0:
                        skip -= 1
                        continue
                    if l == "<hr>" or l == "<hr/>":
                        continue
                    if l.startswith("<!--"):
                        continue
                    if l == """<h1 class="settitle" align="center">ANSI and GNU Common Lisp Document</h1>""":
                        continue
                    if l.startswith("<meta "):
                        continue
                    if l.startswith("<a name=\"") and l.endswith("</a>"):
                        continue
                    if l.startswith("<style"):
                        in_style = True
                        continue
                    if l.startswith("</style"):
                        in_style = False
                        continue
                    if in_style:
                        continue

                    if l.startswith("<link href="):
                        if "rel=\"up\"" in l:
                            n_up            = re.match(".+href=\"([^\"]+?)(#[^\"]+)?\".+", l).group(1)
                            assert(n_up.endswith(".html"))
                            n_up_title      = re.match(".+title=\"([^\"]+)\".+", l).group(1).replace("``", "\"").replace("''", "\"")
                            if n_up_title == "(dir)":
                                n_up         = None
                                n_up_title   = "-"
                        if "rel=\"next\"" in l:
                            n_next          = re.match(".+href=\"([^\"]+?)(#[^\"]+)?\".+", l).group(1)
                            assert(n_next.endswith(".html"))
                            n_next_title    = re.match(".+title=\"([^\"]+)\".+", l).group(1).replace("``", "\"").replace("''", "\"")
                        if "rel=\"prev\"" in l:
                            n_prev          = re.match(".+href=\"([^\"]+?)(#[^\"]+)?\".+", l).group(1)
                            assert(n_prev.endswith(".html"))
                            n_prev_title    = re.match(".+title=\"([^\"]+)\".+", l).group(1).replace("``", "\"").replace("''", "\"")
                            if n_prev_title == "(dir)":
                                n_prev          = None
                                n_prev_title    = "-"
                    
                    if l.startswith("<div class=\"header\""):
                        in_header = True
                        continue
                    if in_header and l.startswith("</div>"):
                        in_header = False
                        continue
                    if in_header:
                        continue

                    if l.startswith("<title>"):
                        l       = l.replace(" (ANSI and GNU Common Lisp Document)", "")
                        title   = re.match("<title>(.+)</title>", l).group(1)
                        l       = l.replace("</title>", " (CLCS)</title>")

                        nodes.append((title, f.replace(".html", "")))


                    # take the very first header as page header
                    if (l.startswith("<h3 ") or l.startswith("<h4 ") or l.startswith("<h2") or l.startswith("<h1")) and section_cnt == 0:
                        l = re.sub(r">\d+(\.\d+){0,4} ", ">", l)
                        out.append("<div class=\"section top-most\">")
                        m = re.match(r".+\[(.+)\].*", l)
                        if m is not None:
                            out.append(f"<div class=\"node-type\">{m.group(1)}</div>")
                            l = re.sub(r"\[(.+)\]", "", l)
                        if "," in l:
                            tline = re.sub("<h[23456] class=\"(sub)?(sub)?section\">", "", l)
                            tline = re.sub("</h[23456]>", "", tline)
                            tline = re.sub("&(gt|GT);", ">", tline)
                            tline = re.sub("&(lt|LT);", "<", tline)
                            keywords = [t.strip() for t in tline.split(",")]
                            for k in keywords:
                                if k != title and len(k.strip()) > 0:
                                    nodes.append((k, f.replace(".html", "")))
                        out.append(l)
                       
                        in_section  = True
                        section_cnt += 1
                        continue


                    elif l.startswith("<h4 ") or l.startswith("<h3 "):
                        if in_section:
                            out.append("</div>")
                        out.append("<div class=\"section\">")
                        l           = re.sub("::<", "<", l)
                        out.append(l)
                        in_section  = True
                        section_cnt += 1
                        continue
                    

                    if l.startswith("</pre>"):
                        out.append("</code>")
                    if l.startswith("<pre class=\"example\">") or l.startswith("<pre>"):
                        l = re.sub("<pre( class=\"example\")?>", "<pre\\1><code>", l)
                        out.append(l)
                        continue

                    if "<tr><td align=\"left\" valign=\"top\">&bull; " in l:
                        l = l.replace("&bull; ", "")
                        l = l.replace("</a>:</td>", "</a></td>")
                        l = l.replace("``", "\"")
                    
                    # table start
                    if re.match(r"(</p>)?<p>.+<!-- /@w -->", l) and not "&nbsp;Figure" in l:
                        in_table = True
                        out.append("<table>")
                        l = re.sub("<p>", "", l)
                        l = re.sub("<!-- /@w -->", "", l)
                        l = re.sub("(&nbsp;){2,}", "</td><td>", l)
                        l = f"<tr><td>{l}</td></tr>"
                        l = re.sub("<td> *</td>", "", l)
                        l = re.sub(r"<p>\s*</p>", "", l)

                    # table caption
                    if re.match(r"(</p>)?<p>(&nbsp;)+Figure.+", l):
                        l = re.sub("</?p>", "", l)
                        l = re.sub("<!-- /@w -->", "", l)
                        l = re.sub("(&nbsp;)+", " ", l)
                        l = f"<div class=\"table-subcaption\">{l}</div>"
                        out.append(l)
                        skip = 1
                        continue

                    if re.match(r"(&nbsp;)+Figure.+", l):
                        l = re.sub("<!-- /@w -->", "", l)
                        l = re.sub("(&nbsp;)+", " ", l)
                        l = f"<div class=\"table-subcaption\">{l}</div>"
                        out.append(l)
                        continue

                    if in_table and re.match(r".+<!-- /@w -->", l):
                        l = re.sub("<!-- /@w -->", "", l)
                        l = re.sub("(&nbsp;){2,}", "</td><td>", l)
                        l = f"<tr><td>{l}</td></tr>"
                        l = re.sub("<td> *</td>", "", l)
                        l = re.sub(r"<p>\s*</p>", "", l)


                    if l.startswith("</p>") and in_table:
                        in_table = False
                        out.append("</table>")
                        continue

                    m = re.match("^(?:<p>)?&lsquo;([^;]+); [^&]+&rsquo;$", l)
                    if m:
                        possible_ref = m.group(1)
                        possible_ref_esc = possible_ref.replace("-", "_002d")
                        if f"{possible_ref_esc}.html" in all_fnames:
                            if l.startswith("<p>"):
                                l = re.sub("&lsquo;(.+)&rsquo;", f"""<a href="{possible_ref_esc}.html">\\1</a>""", l)

                    if l == ", " or l == ",":
                        out[-1] += ", "
                        continue

                    if l.startswith("</body>"):
                        if in_section:
                            out.append("</div>")
                        out.append("<div class=\"bl-placeholder\"></div>")
                    
                    out.append(l)
                    

                    if l.startswith("<head"):
                        out.append("<meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\">")
                        out.append("<link rel=\"icon\" type=\"image/x-icon\" href=\"/favicon.ico\">")
                        out.append("<link rel=\"stylesheet\" href=\"/styles.css\">")
                        out.append("<link rel=\"stylesheet\" href=\"/highlight-lisp/themes/github.css\">")
                        out.append("<script defer src=\"/scripts.js\"></script>")

                    if l.startswith("<body "):
                        
                        prev_disabled   = "disabled" if n_prev is None else ""
                        up_disabled     = "disabled" if n_up is None else ""
                        next_disabled   = "disabled" if n_next is None else ""

                        out.append(f"""
                            <div class="top-wrapper">
                                <div class="top">
                                    <div class="search">
                                        <svg height="20" width="20" viewBox="0 0 512 512"><path d="M221.09 64a157.09 157.09 0 10157.09 157.09A157.1 157.1 0 00221.09 64z" fill="none" stroke="currentColor" stroke-miterlimit="10" stroke-width="32"/><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-miterlimit="10" stroke-width="32" d="M338.29 338.29L448 448"/></svg>
                                        <input type="text" oninput="search(event)" onkeydown="searchKeydown(event)" placeholder="Search for pages">
                                        <div id="search__drop" onblur="hideSearch()"></div>
                                    </div>
                                    <a class="index-btn" href="index.html">
                                        <svg height="20" width="20" viewBox="0 0 512 512"><title>Index</title><path d="M80 212v236a16 16 0 0016 16h96V328a24 24 0 0124-24h80a24 24 0 0124 24v136h96a16 16 0 0016-16V212" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32"/><path d="M480 256L266.89 52c-5-5.28-16.69-5.34-21.78 0L32 256M400 179V64h-48v69" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32"/></svg>
                                    </a>
                                </div>
                            </div>
                            <div class="nav">
                                <a href="{n_prev}" class="nav-btn nav__prev {prev_disabled}">
                                    <svg height="14" width="14" viewBox="0 0 512 512"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="48" d="M328 112L184 256l144 144"/></svg>
                                    {n_prev_title or "-"}
                                </a>
                                <a href="{n_up}" class="nav-btn nav__up {up_disabled}">
                                    <svg height="14" width="14" viewBox="0 0 512 512"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="48" d="M112 328l144-144 144 144"/></svg>
                                    {n_up_title  or "-"}
                                </a>
                                <a href="{n_next}" class="nav-btn nav__next {next_disabled}">
                                    {n_next_title  or "-"}
                                    <svg height="14" width="14" viewBox="0 0 512 512"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="48" d="M184 112l144 144-144 144"/></svg>
                                </a>
                            </div>
                        """)
                    if l.startswith("</body>"):
                        out.append("""<script type="text/javascript" src="/highlight-lisp/highlight-lisp.js"></script>""")

        

        text = "\n".join(out)
        all_refs = re.finditer(r"<a href=\"([^\"]+).html(?:#[^\"]+)?\">([^<]+)</a>", text)
        key = f.replace(".html", "")
        for r in all_refs:
            ref     = r.group(1)
            label   = r.group(2)
            assert(label is not None)
            assert(len(label) > 0)
            keys_to_label[ref] = label
            if not ref in backlinks:
                backlinks[ref] = []
            if not key in backlinks[ref]:
                backlinks[ref].append(key)

        to_write.append((outpath, key, text))
    
    for outpath, key, text in to_write:
        if key in backlinks:
            bl_list = "".join([f"<a href=\"{bl}.html\">{keys_to_label.get(bl, bl)}</a>, " for bl in backlinks[key] if bl != "index"])
            bl_list = bl_list[:-2]
            bl_sec  = f"""
                    <div class="section">
                        <h3>Backlinks</h3>
                        {bl_list}
                    </div>
                """ if len(bl_list) > 0 else ""
            text = text.replace("<div class=\"bl-placeholder\"></div>", bl_sec)

        with open(outpath, "w", encoding="utf-8") as outf:
            outf.write(text)

    with open(os.path.join(folder_path(), "scripts.js"), "r", encoding="utf-8") as fscripts:
        scripts = fscripts.read()

    nodelist    =  ",".join(["['{}','{}']".format(t[0].replace("'", "\\'").replace("``", "\"").replace("''", "\""), t[1].replace("'", "\\'")) for t in nodes])
    scripts     = scripts.replace("{{nodes}}", nodelist)
    
    with open(os.path.join(folder_path(), "scripts.js"), "w", encoding="utf-8") as fscripts:
        fscripts.write(scripts)
    
    searchable_terms = {}
    for term, file in nodes:
        term = term.replace("&gt;", ">")
        term = term.replace("&lt;", "<")
        searchable_terms[term] = f"{file}.html"

    with open(os.path.join(folder_path(), "searchable_terms.json"), "w") as out:
        out.write(json.dumps(searchable_terms, indent=4))

    print(f"Total: {len(nodes)} pages")
    print("Finished conversion.\nResults can be found in /output.")

main()
# insert_table_links()
# insert_escaped_links()
                

                
       
               
       
