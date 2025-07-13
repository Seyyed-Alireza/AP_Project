var btn = document.getElementById('user_name')
var pop = document.getElementById('viewport')
var drop = document.getElementById('user_box')
var container = document.getElementById('container')

function setLeft() {
    let vw = window.innerWidth
    let cw = container.getBoundingClientRect().width
    if (vw > cw) {
        drop.style.left = ((vw - cw) / 2 + 0) + "px";
    }
    if (vw < cw) {
        drop.style.left = "10px"
    }
    if (vw < 576) {
        drop.style.left = "5px"
    }
}

btn.addEventListener("click", function() {
    pop.style.display = pop.style.display === "block" ? "none": "block";
    pop.style.zIndex = '5'
    setLeft();
    drop.style.display = drop.style.display === "block" ? "none": "block";
});

window.addEventListener("click", function(event) {
    if (!btn.contains(event.target) && !drop.contains(event.target)) {
        pop.style.display = "none"
        pop.style.zIndex = '0'
        drop.style.display = "none";
    }
});


var suggestionsBox = document.getElementById('suggestions');
function setLeftSuggestion() {
    let vw = window.innerWidth
    let btnw = document.querySelector("#container > section.search-bar > form > button")
    var search_box = document.getElementById('search_js');
    suggestionsBox.style.right = `${vw - search_box.getBoundingClientRect().right - 15}px`;
    if (vw < 576) {
        suggestionsBox.style.right = '0px';
    }
    // else if (vw > cw) {
    //     suggestionsBox.style.right = `${0.3 * cw}px`;
    // }
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
    if (drop.style.display === "block") {
        setLeft();
    }
    if (suggestionsBox.style.display === "block") {
        setLeftSuggestion();
    }
});