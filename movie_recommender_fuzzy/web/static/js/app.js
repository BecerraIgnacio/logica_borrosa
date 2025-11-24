document.addEventListener("DOMContentLoaded", () => {
  const flipCards = Array.from(document.querySelectorAll("[data-flip]"));

  flipCards.forEach((card) => {
    card.addEventListener("click", () => {
      card.classList.toggle("flipped");
    });
  });

  const ratingGroups = Array.from(document.querySelectorAll("[data-rating-group]"));
  ratingGroups.forEach((group) => {
    const buttons = Array.from(group.querySelectorAll("[data-rating-value]"));
    // El input hidden puede estar fuera del contenedor, así que lo buscamos en el formulario cercano.
    const form = group.closest("form") || group;
    const scoreInput = form.querySelector('input[name="score"]');

    function setActive(value) {
      buttons.forEach((btn) => {
        const v = Number(btn.dataset.ratingValue);
        btn.classList.toggle("active", v <= value);
      });
      if (scoreInput) {
        scoreInput.value = value;
      }
    }

    buttons.forEach((btn) => {
      btn.addEventListener("mouseenter", () => setActive(Number(btn.dataset.ratingValue)));
      btn.addEventListener("focus", () => setActive(Number(btn.dataset.ratingValue)));
      btn.addEventListener("click", (e) => {
        setActive(Number(btn.dataset.ratingValue));
      });
    });
  });
});
