document.addEventListener('DOMContentLoaded', function () {

    // Animation barres de progression au chargement
    document.querySelectorAll('.nc-kpi-barre, .nc-risque-barre').forEach(function (barre) {
        const largeur = barre.style.width;
        barre.style.width = '0%';
        barre.style.transition = 'width 0s';
        setTimeout(function () {
            barre.style.transition = 'width 1.2s ease';
            barre.style.width = largeur;
        }, 300);
    });

    // Compteur animé sur les valeurs KPI
    document.querySelectorAll('.nc-kpi-valeur').forEach(function (el) {
        const original = el.textContent.trim();
        const isPct = original.includes('%');
        const final = parseFloat(original.replace('%', ''));
        if (isNaN(final)) return;
        let current = 0;
        const step = final / (1200 / 16);
        el.textContent = isPct ? '0%' : '0';
        const timer = setInterval(function () {
            current = Math.min(current + step, final);
            el.textContent = isPct ? current.toFixed(1) + '%' : Math.round(current).toString();
            if (current >= final) { clearInterval(timer); el.textContent = original; }
        }, 16);
    });

    // Hover heatmap
    document.querySelectorAll('.nc-heatmap-cell').forEach(function (cell) {
        cell.addEventListener('mouseenter', function () { this.style.zIndex = '5'; });
        cell.addEventListener('mouseleave', function () { this.style.zIndex = ''; });
    });

    // Actualisation auto toutes les 5 minutes
    setTimeout(function () { window.location.reload(); }, 300000);
});
