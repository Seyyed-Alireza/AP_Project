function toPersianNumber(num) {
    return num.toString().replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
}

function updateRatingOutput(qid) {
    const input = document.getElementById(`rating_input_${qid}`);
    const output = document.getElementById(`rating_output_${qid}`);
    if (input && output) {
        output.textContent = toPersianNumber(input.value);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('input[type="range"]').forEach(input => {
        const idPart = input.id.replace('rating_input_', '');
        updateRatingOutput(idPart);

        const checkbox = document.getElementById(`know_${idPart}`);
        if (checkbox) {
            rangeDisable(idPart);
        }
    });
});

function rangeDisable(qid) {
    const input = document.getElementById(`rating_input_${qid}`);
    const checkbox = document.getElementById(`know_${qid}`);
    const output = document.getElementById(`span_output_${qid}`);

    if (checkbox.checked) {
        input.disabled = true;
        output.style.display = 'none';
        let id_counter = parseInt(qid, 10) + 1;
        while (true) {
            const q = document.getElementById(`rating_input_${id_counter}`);
            if (!q) {
                break;
            }
            if (q.type === "range") {
                break;
            }
            q.required = true;
            q.addEventListener("invalid", function () {
                this.setCustomValidity("لطفاً یک گزینه را انتخاب کنید");
            });
        
            q.addEventListener("input", function () {
                this.setCustomValidity("");
            });
            // radios.forEach(radio => {
            //     radio.addEventListener("invalid", function () {
            //         this.setCustomValidity("لطفاً یک گزینه را انتخاب کنید");
            //     });
          
            //     radio.addEventListener("input", function () {
            //         this.setCustomValidity("");
            //     });
            // });
            const questoin = document.getElementById(`qid_${id_counter}`)
            questoin.style.display = "block";
            id_counter += 1;
        }
    } else {
        input.disabled = false;
        output.style.display = 'inline';
        let id_counter = parseInt(qid, 10) + 1;
        while (true) {
            const q = document.getElementById(`rating_input_${id_counter}`);
            if (!q) {
                break;
            }
            if (q.type === "range") {
                break;
            }
            q.required = false;
            q.setCustomValidity("");
            const questoin = document.getElementById(`qid_${id_counter}`)
            questoin.style.display = "none";
            id_counter += 1;
        }
        updateRatingOutput(qid);
    }
}