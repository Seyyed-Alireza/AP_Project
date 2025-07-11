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
            event.preventDefault(); // جلوگیری از ارسال فرم
            errorMsg.style.display = 'block'; // نمایش پیام خطا
            textarea.focus();
        } else {
            errorMsg.style.display = 'none'; // پنهان‌کردن پیام اگر پر شده بود
        }
    });