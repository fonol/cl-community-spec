function searchKeydown(e) {
    if (e.key === 'Escape') {
        e.target.value = '';
        hideSearch();
    }
}
function search(e) {
    let q = e.target.value;
    if (!q || q.trim().length === 0) {
        hideSearch();
    } else {
        q = q.toLowerCase();
        let res = runSearch(q);
        showSearch(res, q);
    }
}
function runSearch(q) {
    let results = [];
    for (let n of nodes) {
        if (n[0].includes(q)) {
            results.push(n);
        }
    }

    results.sort((n1, n2) => {
        let a = n1[0];
        let b = n2[0];

        if (a === q) {
            return -1;
        }
        if (b === q) {
            return 1;
        }
        // If the search term is at the start of the item, it is more relevant
        if (a.startsWith(q) && !b.startsWith(q)) {
            return -1;
        } 
        if (!a.startsWith(q) && b.startsWith(q)) {
            return 1;
        }

        // If the search term appears earlier in the item, it is more relevant
        if (a.indexOf(q) < b.indexOf(q)) {
            return -1;
        } else if (a.indexOf(q) > b.indexOf(q)) {
            return 1;
        }

        return 0;
    });
    return results;

}
function showSearch(results, q) {
    let drop = document.getElementById('search__drop');
    drop.style.display = 'block';
    let html = '';

    if (results.length === 0) {
        html = '<div>Nothing found, sorry.</div>';
    }
    for (let r of results) {
        let text = r[0].replaceAll(q, '<mark>'+q+'</mark>');
        html += `<a class="search__res" href="${r[1]}.html">${text}</a>`;
    }
    drop.innerHTML = html;
}
function hideSearch() {
    document.getElementById('search__drop').style.display = 'none';
}