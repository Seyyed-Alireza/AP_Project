document.addEventListener("DOMContentLoaded", function() {
    const searchForm = document.querySelector("form.search-form");
    const filterForm = document.querySelector("form.filter-form");
    const hiddenInfo = document.querySelector("form.hidden-info");

    if (searchForm) searchForm.addEventListener("submit", function(e) {
        ["category", "skin_type", "concern", "min_price", "max_price", "sort_by"].forEach(name => {
            const oldInput = searchForm.querySelector(`input[name="${name}"], select[name="${name}"]`);
            if (oldInput && oldInput.type === "hidden") oldInput.remove();
        });

        const brand = filterForm.querySelector("select[name='brand']").value;
        const category = filterForm.querySelector("select[name='category']").value;
        const skin_type = filterForm.querySelector("select[name='skin_type']").value;
        const concern = filterForm.querySelector("input[name='concern']").value;
        const min_price = filterForm.querySelector("input[name='min_price']").value;
        const max_price = filterForm.querySelector("input[name='max_price']").value;
        const sort_by = filterForm.querySelector("select[name='sort_by']").value;

        if (brand) addHiddenInput(searchForm, "brand", brand)
        if (category) addHiddenInput(searchForm, "category", category);
        if (skin_type) addHiddenInput(searchForm, "skin_type", skin_type);
        if (concern) addHiddenInput(searchForm, "concern", concern);
        if (min_price) addHiddenInput(searchForm, "min_price", min_price);
        if (max_price) addHiddenInput(searchForm, "max_price", max_price);
        if (sort_by) addHiddenInput(searchForm, "sort_by", sort_by);
    });

    if (filterForm) filterForm.addEventListener("submit", function(e) {
        const oldQ = filterForm.querySelector("input[name='q']");
        if (oldQ && oldQ.type === "hidden") oldQ.remove();

        const q = searchForm.querySelector("input[name='q']").value
        if (q) addHiddenInput(filterForm, "q", q);
        if (more) addHiddenInput(filterForm, "more", more)
    });

    function addHiddenInput(form, name, value) {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = name;
        input.value = value;
        form.appendChild(input);
    }
});