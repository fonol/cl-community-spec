import os
import re


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

            skip            = 0

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
                if l.startswith("<a name=\""):
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
                    if f == "index.html":
                        l = "<title>CL CommunitySpec (CLCS)</title>"

                    nodes.append((title, f.replace(".html", "")))


                # take the very first header as page header
                if (l.startswith("<h3 ") or l.startswith("<h4 ") or l.startswith("<h2") or l.startswith("<h1")) and section_cnt == 0:
                    l = re.sub(r">\d+(\.\d+){0,4} ", ">", l)
                    out.append("<div class=\"section top-most\">")
                    m = re.match(r".+\[(.+)\].*", l)
                    if m is not None:
                        out.append(f"<div class=\"node-type\">{m.group(1)}</div>")
                        l = re.sub(r"\[(.+)\]", "", l)
                    if f == "index.html":
                        l = "<h1 class=\"main\">Common Lisp CommunitySpec (CLCS)</h1>"
                    out.append(l)
                    if f == "index.html":
                        out.append("""<div class="main-sub">
                            <div>
                                A rendition of the Common Lisp ANSI Specification draft.
                            </div>
                            <a href="https://github.com/fonol/cl-community-spec" title="Source Repository">
                                <svg height="22" width="22" viewBox="0 0 512 512"><path d="M256 32C132.3 32 32 134.9 32 261.7c0 101.5 64.2 187.5 153.2 217.9a17.56 17.56 0 003.8.4c8.3 0 11.5-6.1 11.5-11.4 0-5.5-.2-19.9-.3-39.1a102.4 102.4 0 01-22.6 2.7c-43.1 0-52.9-33.5-52.9-33.5-10.2-26.5-24.9-33.6-24.9-33.6-19.5-13.7-.1-14.1 1.4-14.1h.1c22.5 2 34.3 23.8 34.3 23.8 11.2 19.6 26.2 25.1 39.6 25.1a63 63 0 0025.6-6c2-14.8 7.8-24.9 14.2-30.7-49.7-5.8-102-25.5-102-113.5 0-25.1 8.7-45.6 23-61.6-2.3-5.8-10-29.2 2.2-60.8a18.64 18.64 0 015-.5c8.1 0 26.4 3.1 56.6 24.1a208.21 208.21 0 01112.2 0c30.2-21 48.5-24.1 56.6-24.1a18.64 18.64 0 015 .5c12.2 31.6 4.5 55 2.2 60.8 14.3 16.1 23 36.6 23 61.6 0 88.2-52.4 107.6-102.3 113.3 8 7.1 15.2 21.1 15.2 42.5 0 30.7-.3 55.5-.3 63 0 5.4 3.1 11.5 11.4 11.5a19.35 19.35 0 004-.4C415.9 449.2 480 363.1 480 261.7 480 134.9 379.7 32 256 32z"/></svg>
                            </a>
                        </div>""")
                        out.append("</div>")
                        out.append("<div class=\"section\">")
                        out.append("<h2 class=\"chapter\">Index</h2>")
                        out.append("<pre class=\"menu-comment\">Overview</pre>")
                        section_cnt += 1

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

    print(f"Total: {len(nodes)} pages")
    print("Finished conversion.\nResults can be found in /output.")

main()
# insert_table_links()
# insert_escaped_links()
                

                
       
               
       
