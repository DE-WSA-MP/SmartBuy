document.addEventListener("DOMContentLoaded", () => {
    const defaults = {
        price_weight: 40,
        rating_weight: 30,
        reviews_weight: 20,
        availability_weight: 10
    };

    const sliders = Object.keys(defaults);
    const totalElement = document.getElementById("total_weight");
    const form = document.querySelector(".weights-form");

    if (!form || !totalElement) return;

    function updateWeights() {
        let total = 0;

        sliders.forEach((id) => {
            const slider = document.getElementById(id);
            const valueLabel = document.getElementById(
                id.replace("_weight", "_value")
            );

            const value = Number(slider.value);
            valueLabel.textContent = value;
            total += value;
        });

        totalElement.textContent = total;
    }

    sliders.forEach((id) => {
        document.getElementById(id).addEventListener("input", updateWeights);
    });

    document.getElementById("reset_weights").addEventListener("click", () => {
        sliders.forEach((id) => {
            document.getElementById(id).value = defaults[id];
        });

        updateWeights();
    });

    form.addEventListener("submit", (event) => {
        const total = sliders.reduce(
            (sum, id) => sum + Number(document.getElementById(id).value),
            0
        );

        if (total === 0) {
            event.preventDefault();
            alert("Please give at least one criterion a weight greater than zero.");
        }
    });

    updateWeights();

    
document.querySelectorAll(".score-fill").forEach((bar) => {
    const score = Number(bar.dataset.score);
    const safeScore = Math.min(100, Math.max(0, score || 0));
    bar.style.width = `${safeScore}%`;
});

});