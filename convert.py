import os
import re
import json
import functools

def get_html_files():

    files = [f for f in os.listdir(src_folder_path()) if re.match(r'^.*\.html$', f)]
    return files

def folder_path():
    return os.path.dirname(os.path.realpath(__file__))

def src_folder_path():
    return os.path.join(folder_path(), "html_in/")

def out_folder_path():
    return os.path.join(folder_path(), "html_out/")

def check_for_tag_mismatch(html):
    m = []
    if html.count("<table") != html.count("</table>"):
        m.append("<table>")
    if html.count("<td") != html.count("</td>"):
        m.append("<td>")
    if html.count("<div") != html.count("</div>"):
        m.append("<div>")
    if html.count("<span") != html.count("</span>"):
        m.append("<span>")
    if html.count("<code") != html.count("</code>"):
        m.append("<code>")
    if html.count("<li>") != html.count("</li>"):
        m.append("<li>")
    if html.count("<ul>") != html.count("</ul>"):
        m.append("<ul>")
    if html.count("<ol>") != html.count("</ol>"):
        m.append("<ol>")
    return m

def cleanup(html):

    html  = re.sub(r"<br ?/?>\s*</td>", "</td>", html, flags=re.MULTILINE)
    return html

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
    
    parents             = {}

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
            in_arguments    = False
            in_syntax_table = False

            n_up            = None
            n_prev          = None
            n_next          = None
            n_next_title    = None
            n_up_title      = None
            n_prev_title    = None

            title           = None
            numbering       = None

            skip            = 0
            
            lines           = all_text.split("\n")
            nextl           = None
            if f == "index.html":
                out = lines
            else:
                for ix, l in enumerate(lines):
                    if skip > 0:
                        skip -= 1
                        continue
                    if ix < len(lines) - 1:
                        nextl = lines[ix+1]
                    else:
                        nextl = None
                    if l == "<hr>" or l == "<hr/>":
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
                            nodes[-1] = (nodes[-1][0], nodes[-1][1], n_up, nodes[-1][3])
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

                        nodes.append((title, f.replace(".html", ""), n_up, None))


                    # take the very first header as page header
                    if (l.startswith("<h3 ") or l.startswith("<h4 ") or l.startswith("<h2") or l.startswith("<h1")) and section_cnt == 0:
                        mnum = re.match(r".+>(\d+(\.\d+){0,6}) .+", l, flags= re.MULTILINE)
                        if mnum is not None:
                            numbering = mnum.group(1)
                            nodes[-1] = (nodes[-1][0], nodes[-1][1], nodes[-1][2], numbering)

                        l = re.sub(r">\d+(\.\d+){0,6} ", ">", l)
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
                                    nodes.append((k, f.replace(".html", ""), n_up, None))
                        out.append(l)
                       
                        in_section  = True
                        section_cnt += 1
                        continue

                    elif l.startswith("<h4 ") or l.startswith("<h3 "):
                        if in_section:
                            if in_arguments:
                                out.append("</table>")
                                in_arguments = False
                            if in_syntax_table:
                                for r in range(1, 5):
                                    if "</tr>" in out[-r]:
                                        break
                                    if "<td>" in out[-r]:
                                        out.append("</td></tr>")
                                        break
                                out.append("</table>")
                                in_syntax_table = False
                            out.append("</div>")
                        out.append("<div class=\"section\">")
                        l           = re.sub("::<", "<", l)
                        out.append(l)
                        if re.match(".+(>Arguments|Compound Type Specifier Arguments).+", l):
                            in_arguments = True
                            out.append("""<table class="arguments-table">""")
                        else:
                            in_arguments = False
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

                    if "::=" in l and not "<td" in l and section_cnt == 1 and not in_syntax_table:
                        in_syntax_table = True
                        out.append("""<table class="syntax-table">""")

                    if in_syntax_table:
                        if "::=" in l:
                            for ib in range(10):
                                if "<td>" in out[-ib]:
                                    out.append("</td></tr>")
                                    break
                            l  = re.sub("<!-- /@w -->", "", l)
                            l  = re.sub("^<p>", "", l)
                            c0 = l.split("::=")[0]
                            c1 = re.sub(r"\s+$", "", l.split("::=")[1])
                            out.append(f"<tr><td>{c0}</td><td>::=</td><td>{c1}")
                            continue
                        elif re.match(r"^\s*</p>", l):
                            continue
                        elif "<!--end-syntax-table-->" in l:
                            in_syntax_table = False
                            out.append("</td></tr></table>")
                            continue

                    
                    # table start
                    if re.match(r"(</p>)?<p>.+<!-- /@w -->", l) and not "&nbsp;Figure" in l and not in_syntax_table:
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

                    
                    if in_table and not in_syntax_table and re.match(r".+<!-- /@w -->", l):
                        l = re.sub("<!-- /@w -->", "", l)
                        l = re.sub("(&nbsp;){2,}", "</td><td>", l)
                        l = f"<tr><td>{l}</td></tr>"
                        l = re.sub("<td> *</td>", "", l)
                        l = re.sub(r"<p>\s*</p>", "", l)


                    if l.startswith("</p>") and in_table and not in_syntax_table:
                        in_table = False
                        out.append("</table>")
                        continue

                    if in_arguments: 
                        if "&mdash;" in l or "&ndash;" in l:
                            l = re.sub(r"^\s*<p>", "", l)
                            l = re.sub("&[mn]dash;", "</td><td>", l)
                            l = f"<tr><td>{l}"
                            out.append(l)
                            continue
                        elif re.match(r"^\s*</p>", l):
                            if ("&mdash;" in nextl 
                                or "&ndash;" in nextl 
                                or nextl.startswith("<a")
                                or nextl.startswith("</body")):
                                out.append("</td></tr>")
                                continue
                        elif re.match(r"^\s*<a .*", l):
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

                    if l.startswith("<!--"):
                        continue

                    if l.startswith("</body>"):
                        if in_section:
                            if in_arguments or in_syntax_table:
                                for r in range(5):
                                    if "</tr>" in out[-r]:
                                        break
                                    if "<td>" in out[-r]:
                                        out.append("</td></tr>")
                                        break
                                out.append("</table>")
                            out.append("</div>")
                        out.append("<div class=\"bl-placeholder\"></div>")
                        # close body main
                        out.append("</div>")
                        # close body inner
                        out.append("</div>")
                        # close body main inner
                        out.append("</div>")
                    out.append(l)
                    

                    if l.startswith("<head"):
                        out.append("<meta charset=\"UTF-8\">")
                        out.append("<meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\">")
                        out.append("<link rel=\"icon\" type=\"image/x-icon\" href=\"/favicon.ico\">")
                        out.append("<link rel=\"stylesheet\" href=\"/styles.css\">")
                        out.append("<link rel=\"stylesheet\" href=\"/highlight-lisp/themes/github.css\">")
                        out.append("""<script>
    (() => {
        let savedTheme = localStorage.getItem('clcs-theme');
        let isDarkTheme = false;
        if (savedTheme) {
            isDarkTheme = savedTheme === 'dark';
        } else {
            isDarkTheme = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
        }
        if (isDarkTheme) {
            window._theme = 'dark';
            document.documentElement.setAttribute("data-theme", "dark");
        } else {
            window._theme = 'light';
        }
    })()
</script>""")
                        out.append("<script defer src=\"/scripts.js\"></script>")

                    if l.startswith("<body "):
                        
                        prev_disabled   = "disabled" if n_prev is None else ""
                        up_disabled     = "disabled" if n_up is None else ""
                        next_disabled   = "disabled" if n_next is None else ""

                        out.append(f"""
        <div class="body__inner">
            __nav-placeholder__
            <div class="body__main">
                <div class="body__main__inner">
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
                            <div id="theme-btn--dark" onclick="toggleTheme()" title="Switch to light mode" class="index-btn"><svg viewBox="0 0 24 24" width="20" height="20"><path fill="none" d="M0 0h24v24H0z"/><path fill="currentColor" d="M10 7a7 7 0 0 0 12 4.9v.1c0 5.523-4.477 10-10 10S2 17.523 2 12 6.477 2 12 2h.1A6.979 6.979 0 0 0 10 7zm-6 5a8 8 0 0 0 15.062 3.762A9 9 0 0 1 8.238 4.938 7.999 7.999 0 0 0 4 12z"/></svg></div>
                            <div id="theme-btn--light" onclick="toggleTheme()" title="Switch to dark mode" class="index-btn"><svg viewBox="0 0 24 24" width="20" height="20"><path fill="none" d="M0 0h24v24H0z"/><path fill="currentColor" d="M12 18a6 6 0 1 1 0-12 6 6 0 0 1 0 12zm0-2a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM11 1h2v3h-2V1zm0 19h2v3h-2v-3zM3.515 4.929l1.414-1.414L7.05 5.636 5.636 7.05 3.515 4.93zM16.95 18.364l1.414-1.414 2.121 2.121-1.414 1.414-2.121-2.121zm2.121-14.85l1.414 1.415-2.121 2.121-1.414-1.414 2.121-2.121zM5.636 16.95l1.414 1.414-2.121 2.121-1.414-1.414 2.121-2.121zM23 11v2h-3v-2h3zM4 11v2H1v-2h3z"/></svg></div>
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
                        # remember sidebar scroll position
                        out.append("""
        <script>
            (() => {
                let sidebar = document.querySelector(".sidenav__main");
                let t = localStorage.getItem("sidebar-scroll");
                if (t !== null) {
                    sidebar.scrollTop = parseInt(t, 10);
                }
                window.addEventListener("beforeunload", () => {
                    localStorage.setItem("sidebar-scroll", sidebar.scrollTop);
                });
            })();
        </script>""")
                        out.append("""      <script type="text/javascript" src="/highlight-lisp/highlight-lisp.js"></script>""")

        

        text = "\n".join(out)
        text = cleanup(text)
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
        n = nodes[-1]
        nodes[-1] = (n[0], n[1], n_up, n[3])

    parents = {}
    for title, file, parent, numbering in nodes: 
        if numbering is None:
            continue
        if parent is None or parent == "Top" or parent == "index.html":
            parent = ""
        parent = parent.replace(".html", "")
        if parent not in parents:
            parents[parent] = []
        parents[parent].append((title, file, numbering))
    
    def cmp_nav_item(i1, i2):
        num1 = i1[2]
        num2 = i2[2]
        comps1 = num1.split(".")
        comps2 = num2.split(".")

        if len(comps1) == len(comps2):
            if int(comps1[-1]) > int(comps2[-1]):
                return 1
            if int(comps1[-1]) < int(comps2[-1]):
                return -1
            return 0
        return 0

    def print_nav_item(parents, children):
        html = ""
        for ctitle, cfile, numbering in sorted(children, key=functools.cmp_to_key(cmp_nav_item)):
            cnode = ""
            if cfile in parents:
                cnode = print_nav_item(parents, parents[cfile])
                cnode = f"<ul>{cnode}</ul>"
            ctitle = ctitle.replace("``", "\"")
            html += f"""<li><div><span>{numbering}</span><a href="{cfile}.html">{ctitle}</a></div>{cnode}</li>"""
        return html

    nav = print_nav_item(parents, parents[""])
    nav = f"""<div class="sidenav">
                <div class="sidenav__header"> CLCS 
                    <div title="Scroll to current page" onclick="scrollSidenavToCurrentPage()">
                        <svg viewBox="0 0 24 24" width="22" height="22"><path fill="none" d="M0 0h24v24H0z"/><path fill="currentColor" d="M13 1l.001 3.062A8.004 8.004 0 0 1 19.938 11H23v2l-3.062.001a8.004 8.004 0 0 1-6.937 6.937L13 23h-2v-3.062a8.004 8.004 0 0 1-6.938-6.937L1 13v-2h3.062A8.004 8.004 0 0 1 11 4.062V1h2zm-1 5a6 6 0 1 0 0 12 6 6 0 0 0 0-12zm0 4a2 2 0 1 1 0 4 2 2 0 0 1 0-4z"/></svg>
                    </div> 
                </div>
                <div class="sidenav__main">
                    <ul>{nav}</ul>
                </div>
                <div class="sidenav__footer">
                    <a href="https://github.com/fonol/cl-community-spec">
                        src
                    </a>
                    <a href="https://github.com/fonol/cl-community-spec/issues/new">
                        report error
                    </a>
                </div>
            </div>"""
    mismatched_tags = check_for_tag_mismatch(nav)
    for t in mismatched_tags:
        print(f"WARN: nav has mismatched tag: {t}")
        
    
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

        text = text.replace("__nav-placeholder__", nav)
        mismatched_tags = check_for_tag_mismatch(text)
        for t in mismatched_tags:
            fd = outpath[outpath.rindex("/"):]
            print(f"WARN: File {fd} has mismatched tag: {t}")
        with open(outpath, "w", encoding="utf-8") as outf:
            outf.write(text)

    with open(os.path.join(folder_path(), "scripts.js"), "r", encoding="utf-8") as fscripts:
        scripts = fscripts.read()

    nodelist    =  ",".join(["['{}','{}']".format(t[0].replace("'", "\\'").replace("``", "\"").replace("''", "\""), t[1].replace("'", "\\'")) for t in nodes])
    scripts     = scripts.replace("{{nodes}}", nodelist)
    
    with open(os.path.join(folder_path(), "scripts.js"), "w", encoding="utf-8") as fscripts:
        fscripts.write(scripts)
    
    searchable_terms = {}
    for term, file, _, _ in nodes:
        term = term.replace("&gt;", ">")
        term = term.replace("&lt;", "<")
        searchable_terms[term] = f"{file}.html"

    with open(os.path.join(folder_path(), "searchable_terms.json"), "w") as out:
        out.write(json.dumps(searchable_terms, indent=4))

    print(f"Total: {len(nodes)} pages")
    print("Finished conversion.\nResults can be found in /html_out.")

main()
# insert_table_links()
# insert_escaped_links()
                

                
       
               
       
