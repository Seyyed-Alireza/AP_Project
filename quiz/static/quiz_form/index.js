document.getElementById('skip-btn').addEventListener('click', function(event) {
    event.preventDefault();
    fetch("{% url 'skip_quiz' %}", {
        method: "POST",
        headers: {
            "X-CSRFToken": "{{ csrf_token }}",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({})
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              window.location.href = "{% url 'mainpage' %}";
          } else {
              alert("خطایی رخ داد.");
          }
      });
});