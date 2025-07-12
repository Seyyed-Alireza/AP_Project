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


const ratingInput = document.querySelector('input[name="rating"]');
    const ratingOutput = document.getElementById('rating_output');

    function toPersianNumber(num) {
        return num.toString().replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
    }

    ratingInput.addEventListener('input', () => {
        ratingOutput.textContent = toPersianNumber(ratingInput.value);
    });

    ratingOutput.textContent = toPersianNumber(ratingInput.value);


    document.getElementById('comment_form').addEventListener('submit', function(event) {
        const textarea = this.querySelector('textarea[name="text"]');
        const errorMsg = document.getElementById('error-message');

        if (!textarea.value.trim()) {
            event.preventDefault();
            errorMsg.style.display = 'block';
            textarea.focus();
        } else {
            errorMsg.style.display = 'none';
        }
    });