var suggestionsBox = document.getElementById('suggestions');
var pop = document.getElementById('viewport')
function setLeftSuggestion() {
    let vw = window.innerWidth
    let btnw = document.querySelector("#container > section.search-bar > form > button")
    var search_box = document.getElementById('search_js');
    if (vw < 576) {
        suggestionsBox.style.right = '0px';
    } else {
        suggestionsBox.style.right = `${vw - search_box.getBoundingClientRect().right - 15}px`;
    }
    if (vw < 576) {
        suggestionsBox.style.width = '100%';
    } else {
        suggestionsBox.style.width = `${search_box.getBoundingClientRect().width + btnw.getBoundingClientRect().width + 10}px`;
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('search-input');


    input.addEventListener('input', function () {
        const query = input.value.trim();
        if (query.length === 0) {
            suggestionsBox.innerHTML = '';
            suggestionsBox.style.display = 'none';
            pop.style.display = 'none'
            return;
        }

        fetch(`/live-search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                const results = data.results;
                if (results.length > 0) {

                    // link suggestions to product
                    // suggestionsBox.innerHTML = results.map(p => 
                    //     `<div class="suggestion-item" onclick="location.href='/product/${p.id}/'">${p.name}</div>`
                    // ).join('');
                    // suggestionsBox.style.display = 'block';

                    suggestionsBox.innerHTML = results.map(p => 
                        `<div class="suggestion-item" data-name="${p.name}">${p.name}</div>`
                    ).join('');
                    suggestionsBox.style.display = 'block';
                    pop.style.display = 'block';
                    var searchjs = document.getElementById('search_js')
                    var btnw = document.querySelector("#container > section.search-bar > form > button")
                    searchjs.style.position = 'relative'
                    searchjs.style.zIndex = '5'
                    btnw.style.position = 'relative'
                    btnw.style.zIndex = '5'
                    setLeftSuggestion();
                
                    document.querySelectorAll('.suggestion-item').forEach(item => {
                        item.addEventListener('click', function () {
                            input.value = this.getAttribute('data-name');
                            input.form.submit();
                        });
                    });
                } else {
                    suggestionsBox.innerHTML = '<div class="suggestion-item">موردی یافت نشد</div>';
                    suggestionsBox.style.display = 'block';
                    pop.style.display = 'block';
                    var searchjs = document.getElementById('search_js')
                    var btnw = document.querySelector("#container > section.search-bar > form > button")
                    searchjs.style.position = 'relative'
                    searchjs.style.zIndex = '5'
                    btnw.style.position = 'relative'
                    btnw.style.zIndex = '5'
                    setLeftSuggestion();
                }
            });
    });

    document.addEventListener('click', function (event) {
        if (!input.contains(event.target) && !suggestionsBox.contains(event.target)) {
            suggestionsBox.style.display = 'none';
            var searchjs = document.getElementById('search_js')
            var btnw = document.querySelector("#container > section.search-bar > form > button")
            searchjs.style.position = 'static'
            searchjs.style.zIndex = '0'
            btnw.style.position = 'static'
            btnw.style.zIndex = '0'
        }
    });
});


window.addEventListener("resize", function() {
    if (suggestionsBox.style.display === "block") {
        setLeftSuggestion();
    }
});