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
    if (vw < 1360) {
        drop.style.left = "10px"
    }
    if (vw < 576) {
        drop.style.left = "5px"
    }
}

btn.addEventListener("click", function() {
    pop.style.display = pop.style.display === "block" ? "none": "block";
    setLeft();
    drop.style.display = drop.style.display === "block" ? "none": "block";
});

window.addEventListener("click", function(event) {
    if (!btn.contains(event.target) && !drop.contains(event.target)) {
        pop.style.display = "none"
        drop.style.display = "none";
    }
});

window.addEventListener("resize", function() {
    if (drop.style.display === "block") {
        setLeft();
    }
});