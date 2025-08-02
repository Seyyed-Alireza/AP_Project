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
            console.log('here')
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
    } else {
        input.disabled = false;
        output.style.display = 'inline'
        updateRatingOutput(qid);
    }
}