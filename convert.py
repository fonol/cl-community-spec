import os
import re
import json

nnames = {}

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <title>{{title}}</title>
  <meta property="og:title" content="{{title}}">
  <meta property="og:type" content="website">

  <link rel="stylesheet" href="/styles.css">
  <script defer src="/scripts.js"></script>
  <link rel="stylesheet" href="/highlight-lisp/themes/github.css">
</head>
<body>
    <main>
        <div class="top">
            <div class="search">
                <svg height="20" width="20" viewBox="0 0 512 512"><path d="M221.09 64a157.09 157.09 0 10157.09 157.09A157.1 157.1 0 00221.09 64z" fill="none" stroke="currentColor" stroke-miterlimit="10" stroke-width="32"/><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-miterlimit="10" stroke-width="32" d="M338.29 338.29L448 448"/></svg>
                <input type="text" oninput="search(event)" onkeydown="searchKeydown(event)" placeholder="Search for pages">
                <div id="search__drop" onblur="hideSearch()"></div>
            </div>
            <a class="index-btn" href="{{top}}.html">
                <svg height="20" width="20" viewBox="0 0 512 512"><title>Index</title><path d="M80 212v236a16 16 0 0016 16h96V328a24 24 0 0124-24h80a24 24 0 0124 24v136h96a16 16 0 0016-16V212" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32"/><path d="M480 256L266.89 52c-5-5.28-16.69-5.34-21.78 0L32 256M400 179V64h-48v69" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32"/></svg>
            </a>
        </div>
        {{body}}
    </main>
</body>
<script type="text/javascript" src="/highlight-lisp/highlight-lisp.js"></script>
<script>
    window.nodes = [{{node_list}}];
    for (let el of document.getElementsByTagName('code')) {
        el.innerHTML = el.innerHTML.replace(/<br>/g, '\\n');
        HighlightLisp.highlight_element(el);
    }
</script>
</html>
"""

def get_info_files():

    files = [f for f in os.listdir(info_folder_path()) if re.match(r'^.*\.info-[0-9]+$', f)]
    return files

def to_json(text, all_nodes):
    lines = text.split("\n")

    inside  = ""
    last_el = ""
    syn_name = ""

    # elements to fill
    node = {
        "name": "",
        "prev": "",
        "next": "",
        "up": "",
        "header": {
            "type": None,
            "text": None
        },
        "sections": [],
        "_otext": text
        
    } 
    chunk = ""
    sec = {
        "type": "",
        "text": ""
    }
    cur_argv = ""

    ix      = -1
    while ix < len(lines)-1:
        ix      += 1
        l       = lines[ix]
        nextl   = lines[ix+1] if ix < len(lines)-1 else None

        # navigation
        m = re.match(r"^File: .+?\.info,\s+Node:\s+(.+?),(:?\s+(?:Prev|Next):\s+(.+),)?", l)
        if m is not None:
            node["name"] = m.group(1).replace("''", "\"").replace("``", "\"")
            pm = re.match(r".+Prev:\s+(?P<p>[^,]+)(,.+|$)", l, flags=re.DOTALL)
            node["prev"] = pm.group("p").replace("''", "\"").replace("``", "\"") if pm is not None else None
            if node["prev"] == "(dir)":
                node["prev"] = None
            nm = re.match(r".+Next:\s+(?P<n>[^,]+)(,.+|$)", l, flags=re.DOTALL)
            node["next"] = nm.group("n").replace("''", "\"").replace("``", "\"") if nm is not None else None
            if node["next"] == "(dir)":
                node["next"] = None
            nu = re.match(r".+Up:\s+(?P<u>[^,]+)(,.+|$)", l, flags=re.DOTALL)
            node["up"] = nu.group("u").replace("''", "\"").replace("``", "\"") if nu is not None else None
            if node["up"] == "(dir)":
                node["up"] = None
            continue

        if nextl is not None and re.match("^[-*=]{4,}", nextl):
            m = re.match(r"^(.+?)(?:\s+\[(.+)\])?$", l)
            if m is not None:
                node["header"]["type"] = m.group(2)
            else:
                node["header"]["type"] = ""

            node["header"]["text"] = m.group(1).strip().replace("''", "\"").replace("``", "\"")
            ix          += 1
            last_el     = "header"
            continue

        # syntax
        m = re.match("^`(.+)' ", l)
        if m is not None:
            syn_group   = m.group(1)
            rest        = re.sub("^`(.+)' ", "", l)
            inside      = "syn-group"
            chunk       = rest
            sec         = {
                "type": "Syntax",
                "defs": [],
                "text": ""
            }
            while  ix < len(lines) -1 and not is_subheader(lines, ix):
                ix += 1
                m = re.match("^`(.+)' ", lines[ix])
                if m is not None:
                    sec["defs"].append({
                        "name": syn_group.strip(),
                        "text": chunk
                    })
                    syn_group   = m.group(1)
                    rest        = re.sub("^`(.+)' ", "", lines[ix])
                    chunk       = rest + "\n"
                else:
                    if ix < len(lines) -1 and not is_subheader(lines,  ix):
                        chunk += lines[ix] + "\n"

            sec["defs"].append({
                "name": syn_group.strip(),
                "text": chunk
            })
        if is_subheader(lines, ix):
            subh_name   = subheader_name(lines, ix)
            inside      = subh_name 

            if len(sec) > 0:
                node["sections"].append(sec)
            sec       = {
                "type": subh_name,
                "text": ""
            }
            chunk = ""
            ix += 1
            continue
        
        # todo: handle special re-occurring sections
        if inside is not None and len(l.strip()) > 0:
            if inside == "Arguments and Values":
                if not "--" in l:
                    chunk += l + "\n"
                else:
                    if not "values" in sec:
                        sec["values"] = []
                    if len(chunk) > 0 and cur_argv != "":
                        sec["values"].append({
                            "name": cur_argv,
                            "desc": chunk
                        })
                        chunk = ""

                    ix_sep      = l.index("--")
                    cur_argv    = l[0:ix_sep]
                    chunk       = l[ix_sep+2:]
                    if next_is_subheader_or_end(lines, ix+1) or is_empty_or_end(lines, ix+1):
                        sec["values"].append({
                            "name": cur_argv,
                            "desc": chunk
                        })
            elif inside == "Class Precedence List":
                items = l.split(",")
                sec["items"] = []
                for i in items:
                    sec["items"].append({
                        "name": i,
                        "link": nname(i) if i in all_nodes else None
                    })
            else:
                sec["text"] += l + "\n"

    if len(sec) > 0:
        node["sections"].append(sec)

    return node


def is_empty_or_end(lines, ix):
    if ix == len(lines) -1:
        return True
    return len(lines[ix+1].strip()) == 0

def is_subheader(lines, ix):
    if ix == len(lines) -1:
        return False
    return len(lines[ix].strip()) > 0 and re.match(r"^\.{2,}", lines[ix+1])

def next_is_subheader_or_end(lines, ix):
    if ix == len(lines) -1:
        return True
    while ix < len(lines) - 1:
        ix +=1 
        if is_subheader(lines, ix):
            return True
        if len(lines[ix].strip()) > 0:
            return False
    return True

def subheader_name(lines, ix):
    name = re.match(r"^(.+)", lines[ix]).group(1).strip()
    if name.endswith("::"):
        name = name[:-2]
    return name

def folder_path():
    return os.path.dirname(os.path.realpath(__file__))

def info_folder_path():
    return os.path.join(folder_path(), "info/")

def out_folder_path():
    return os.path.join(folder_path(), "output/")

def escape_html(text):
    text =  text.replace("<=", "&lte;")
    text =  text.replace(">=", "&gte;")
    text =  text.replace(">", "&gt;")
    text =  text.replace("<", "&lt;")
    return text

def nname(text):
    global nnames 
    if text in nnames:
        return nnames[text]
    if text == "*":
        return "asterisk"
    if text == "+":
        return "plus"
    if text == "-":
        return "minus"
    if text == "/":
        return "div"
    if text == "=":
        return "eq"
    if text == "do; do*":
        return "do"
    if text == "let; let*":
        return "let"
    text    = text.replace("->", "-arr-")
    text    = text.replace("*", "-ast-")
    text    = text.replace("\"", "-dquot-")
    text    = text.replace("\'", "-squot-")
    h       = "".join([c for c in text if c.isalpha() or c.isdigit() or c==' ' or c=='-']).rstrip()
    nnames[text] = h
    return h

    
def to_html(node_dict, node_list): 

    nd              = node_dict

    prev_disabled   = "disabled" if nd["prev"] is None or nd["prev"] == "" else ""
    up_disabled     = "disabled" if nd["up"] is None or nd["up"] == "" else ""
    next_disabled   = "disabled" if nd["next"] is None or nd["next"] == "" else ""
    n_prev          = (nd.get("prev", "-") or "-").strip()
    n_next          = (nd.get("next", "-") or "-").strip()
    n_up            = (nd.get("up", "-") or "-").strip()

    l_prev          = nname(n_prev)
    l_next          = nname(n_next)
    l_up            = nname(n_up)



    body = f"""
        <div class="nav">
            <a href="{l_prev}.html" class="nav-btn nav__prev {prev_disabled}">
                <svg height="14" width="14" viewBox="0 0 512 512"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="48" d="M328 112L184 256l144 144"/></svg>
                {n_prev}
            </a>
            <a href="{l_up}.html" class="nav-btn nav__up {up_disabled}">
                <svg height="14" width="14" viewBox="0 0 512 512"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="48" d="M112 328l144-144 144 144"/></svg>
                {n_up}
            </a>
            <a href="{l_next}.html" class="nav-btn nav__next {next_disabled}">
                {n_next}
                <svg height="14" width="14" viewBox="0 0 512 512"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="48" d="M184 112l144 144-144 144"/></svg>
            </a>
        </div>
        <div class="node-header">
            <div class="node-header__type">{nd["header"]["type"] or ""}</div>
            {nd["header"]["text"] or "Index"}
        </div>
    """

    if node_dict["sections"] is not None:
        for s in node_dict["sections"]:
            stext = s["text"] if "text" in s and s["text"] is not None else None 
            if stext is not None:
                # * Menu: -> h3
                stext = re.sub(r"^\s*\*\s+(.+?[^:\n]):(\r\n|\n|\r|$)", "<h3>\\1</h3>\n", stext, flags=re.MULTILINE)
                stext = re.sub(r"(?:^|\r\n|\n|\r)\s*\*\s+([^ ].*?)::(\r\n|\n|\r|$)", "<a class=\"link-block\" href=\"\\1\">\\1</a>", stext, flags=re.MULTILINE)
                # inline links 
                stext = re.sub(r"\*Note[ \n]((?:[^:]|\n){1,100})::", "<a href=\"\\1\">\\1</a>", stext, flags=re.MULTILINE)

                # code
                lines       = stext.split("\n")
                last_indent = 0
                in_pre      = False
                pre_six     = -1
                pre_sindent = 0

                for (ix, l) in enumerate(lines):
                    indent = len(l) - len(l.lstrip())
                    if indent - last_indent > 3 and (l.lstrip().startswith(";") or l.lstrip().startswith("(")):
                        if not in_pre:
                            pre_sindent = indent
                            pre_six = ix
                        in_pre = True
                    elif in_pre and indent - pre_sindent < -3:
                        pre_content = "\n".join(lines[pre_six:ix])
                        if pre_content.count("(") > 0 and pre_content.count(")") > 0:
                            min_indent = 100
                            for l in lines[pre_six:ix]:
                                lindent = len(l) - len(l.lstrip())
                                if len(l.strip()) > 0 and lindent < min_indent:
                                    min_indent = lindent
                            for lix in range(pre_six,ix):
                                if len(lines[lix]) > 0:
                                    lines[lix] = lines[lix][min_indent:]
                            lines[pre_six] = "<pre><code>"+ lines[pre_six]
                            lines[ix-1] = lines[ix-1] + "</code></pre>"
                        in_pre = False
                    last_indent = indent

                stext = "\n".join(lines)


                stext = re.sub("<a href=\"([^\n\"]+)\n([^\n\"]+)\">", "<a href=\"\\1 \\2\">", stext)
                for n in node_list:
                    stext = stext.replace(f"href=\"{n}\"", f"href=\"{nname(n)}.html\"")
                stext = stext.replace(f"href=\"let; let*\"", "href=\"let.html\"")
                stext = stext.replace(f"href=\"flet; labels; macrolet\"", "href=\"flet.html\"")
                stext = stext.replace(f"href=\"do; do*\"", "href=\"let.html\"")
                stext = stext.replace(f"href=\"documentation; (setf documentation)\"", "href=\"documentation.html\"")
                stext = re.sub("\n\s+\n", "<br><br>", stext, re.MULTILINE)
                stext = stext.replace("\n", "<br>")

            section_html = ""
            if s["type"] == "Syntax":
                if "defs" in s:
                    for d in s["defs"]:
                        text = escape_html(d["text"])
                        text = text.replace("\n", "<br>")
                        section_html = f"""
                            {section_html}
                            <div class="syntax__def">
                                <code class="syntax__def-header">{d["name"]}</code>
                                <div class="syntax__def-body">{text}</div>
                            </div>
                        """
                if stext is not None and len(stext) > 0:
                    section_html = f"""
                        {section_html}
                        <div>
                            {stext}
                        </div>
                    """
            elif s["type"] == "Arguments and Values":
                section_html+= "<table>"
                for v in s["values"]:
                    section_html += f"""
                    <tr class="argv-row">
                        <td>
                            <code>{v["name"]}</code>
                        </td>
                        <td>
                            <div class="argv-desc">{v["desc"]}</div>
                        </td>
                    </tr>"""
                section_html+= "</table>"
            elif s["type"] == "Class Precedence List":
                for v in s["items"]:
                    if v["link"] is not None:
                        section_html += f"""
                            <a href="{v["link"]}.html">{v["name"]}</a>
                        """
                    else:
                        section_html += f"""
                            <span>{v["name"]}</span>
                        """
            else:
                section_html = stext

            if len(section_html) > 0:
                body = f"""
                    {body}
                    <div class="section">
                        <div class="section__header">{s["type"]}</div>
                        {section_html}
                    </div>
                """

    node_list =  ",".join(["['{}', '{}']".format(n.replace("'", "\\'").lower(), nname(n)) for n in node_list])
    return (HTML_TEMPLATE
                .replace("{{body}}", body)
                .replace("{{title}}", node_dict["name"])
                .replace("{{node_list}}", node_list)
                .replace("{{top}}", nname("Top"))
                )

def main():
    files               = get_info_files()
    all_nodes_found     = {}
    all_sections        = []
    all_node_names      = []

    for f in files:
        fpath = os.path.join(info_folder_path(), f)
        lines_col       = []
        sections        = []
        with open(fpath, 'r') as r:
            in_sec = False
            for l in r.readlines():
                if l.startswith(""):
                    in_sec = True
                    if len(lines_col) > 0:
                        sections.append("".join(lines_col))
                        lines_col  = []
                elif in_sec:
                    lines_col.append(l)
            if len(lines_col) > 0:
                sections.append("".join(lines_col))
        all_sections += sections
        print(f"Found {len(sections)} sections in file {f}")

    for s in all_sections:
        match = re.match(r"^File: .+?\.info,\s+Node:\s+(.+?),\s+(Next|Prev):", s)
        if match is None:
            print(f"Warning: Could not match node in section:")
            print(s)
        node                = match.group(1).strip().replace("''", "\"").replace("``", "\"")
        all_node_names.append(node)

    for s in all_sections:
        match               = re.match(r"^File: .+?\.info,\s+Node:\s+(.+?),\s+(Next|Prev):", s)
        node                = match.group(1).strip().replace("''", "\"").replace("``", "\"")
        node_nname            = nname(node)
        node_dict           = to_json(s, all_node_names)
        all_nodes_found[node] = node_dict

        with open(os.path.join(out_folder_path(), "json/", f"{node_nname}.json"), "w",  encoding="UTF-8") as out:
            pprint = json.dumps(node_dict, indent=4)
            out.write(pprint)
            
    print("Generating HTML...")
    for (node, node_dict) in all_nodes_found.items():
        html                = to_html(node_dict, all_node_names)
        node_nname            = nname(node)
        with open(os.path.join(out_folder_path(), f"{node_nname}.html"), "w",  encoding="UTF-8") as out:
            out.write(html)
            
    assert("*print-circle*" in all_node_names)
    assert("Top" in all_node_names)
    assert("The \"Affected By\" Section of a Dictionary Entry" in all_node_names)

    print("Finished conversion.\nResults can be found in /output")
# print(nname("Top"))
main()
                
