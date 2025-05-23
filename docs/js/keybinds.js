document.addEventListener("keydown", function (event) {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();

    const searchInput = document.querySelector("input.md-search__input");

    if (searchInput) {
      searchInput.focus();
      searchInput.select();
    }
  }
});
