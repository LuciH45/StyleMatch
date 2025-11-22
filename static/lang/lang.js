async function loadLanguage(section) {
    const lang = localStorage.getItem("lang") || navigator.language.split("-")[0];
    const selectedLang = ["es", "en"].includes(lang) ? lang : "es";

    const response = await fetch(`/static/lang/${section}/${selectedLang}.json`);
    const data = await response.json();

    // Cambiar <title>
    if (data.title) {
        document.title = data.title;
    }

    // Cambiar textos
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (data[key]) {
            el.textContent = data[key];
        }
    });
}
