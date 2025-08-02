var btn = document.getElementById('user_name');
var pop = document.getElementById('viewport');
var drop = document.getElementById('user_box');
var container = document.getElementById('container');

function setLeft() {
    let vw = window.innerWidth;
    let cw = container.getBoundingClientRect().width;
    if (vw > cw) drop.style.left = ((vw - cw) / 2) + "px";
    if (vw < 1360) drop.style.left = "10px";
    if (vw < 576) drop.style.left = "5px";
}

if (btn && pop && drop) {
    btn.addEventListener("click", function () {
        pop.style.display = pop.style.display === "block" ? "none" : "block";
        setLeft();
        drop.style.display = drop.style.display === "block" ? "none" : "block";
    });

    window.addEventListener("click", function (event) {
        if (!btn.contains(event.target) && !drop.contains(event.target)) {
            pop.style.display = "none";
            drop.style.display = "none";
        }
    });

    window.addEventListener("resize", function () {
        if (drop.style.display === "block") setLeft();
    });
}

const ratingInput = document.querySelector('input[name="rating"]');
const ratingOutput = document.getElementById('rating_output');

if (ratingInput && ratingOutput) {
    function toPersianNumber(num) {
        return num.toString().replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
    }

    ratingInput.addEventListener('input', () => {
        ratingOutput.textContent = toPersianNumber(ratingInput.value);
    });

    ratingOutput.textContent = toPersianNumber(ratingInput.value);
}

const commentForm = document.getElementById('comment_form');
if (commentForm) {
    commentForm.addEventListener('submit', function (event) {
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
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.like-ico').forEach(icon => {
        icon.addEventListener('click', () => {
            icon.classList.toggle('active');
        });
    });
});

// AJAX for like
const likeButton = document.getElementById('like');
if (likeButton) {
    likeButton.addEventListener('click', function (event) {
        event.preventDefault();

        const productId = this.dataset.productId;

        fetch(`/like/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
        .then(response => {
            if (!response.ok) throw new Error('خطا در ارسال لایک');
            return response.json();
        })
        .then(data => {
            const likeCountSpan = document.getElementById('like-count');
            if (likeCountSpan) {
                likeCountSpan.dataset.raw = data.likes;
                const formatted = toPersianDigits(addComma(data.likes));
                likeCountSpan.textContent = formatted;
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
}

function toPersianDigits(str) {
    const persianMap = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    };
    return str.replace(/\d/g, d => persianMap[d]);
}

function addComma(n) {
    return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
