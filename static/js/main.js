/* ========================================
   SMART FASHION INVENTORY - MAIN JS
   ======================================== */

document.addEventListener('DOMContentLoaded', function () {

    // ====== SIDEBAR TOGGLE ======
    const sidebar = document.getElementById('sidebar');
    const mainWrapper = document.getElementById('mainWrapper');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarClose = document.getElementById('sidebarClose');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function () {
            if (window.innerWidth < 992) {
                sidebar.classList.toggle('show');
                sidebarOverlay.classList.toggle('show');
            } else {
                sidebar.classList.toggle('collapsed');
                mainWrapper.classList.toggle('expanded');
            }
        });
    }

    if (sidebarClose) {
        sidebarClose.addEventListener('click', function () {
            sidebar.classList.remove('show');
            sidebarOverlay.classList.remove('show');
        });
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function () {
            sidebar.classList.remove('show');
            sidebarOverlay.classList.remove('show');
        });
    }

    // ====== PROFILE DROPDOWN ======
    const profileTrigger = document.getElementById('profileTrigger');
    const profileMenu = document.getElementById('profileMenu');

    if (profileTrigger && profileMenu) {
        profileTrigger.addEventListener('click', function (e) {
            e.stopPropagation();
            profileMenu.classList.toggle('show');
        });

        document.addEventListener('click', function () {
            profileMenu.classList.remove('show');
        });
    }

    // ====== FULLSCREEN ======
    const fullscreenBtn = document.getElementById('fullscreenBtn');
    if (fullscreenBtn) {
        fullscreenBtn.addEventListener('click', function () {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
                fullscreenBtn.classList.replace('fa-expand', 'fa-compress');
            } else {
                document.exitFullscreen();
                fullscreenBtn.classList.replace('fa-compress', 'fa-expand');
            }
        });
    }

    // ====== AUTO DISMISS ALERTS ======
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) closeBtn.click();
        }, 4000);
    });

    // ====== GLOBAL SEARCH ======
    const globalSearch = document.getElementById('globalSearch');
    if (globalSearch) {
        globalSearch.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                const query = this.value.trim();
                if (query) {
                    window.location.href = '/products/?q=' + encodeURIComponent(query);
                }
            }
        });
    }

    // ====== LOAD DASHBOARD CHARTS ======
    if (document.getElementById('categoryChart')) {
        loadDashboardCharts();
    }

    // ====== LOAD REPORT CHARTS ======
    if (document.getElementById('reportCategoryChart')) {
        loadReportCharts();
    }

    // ====== ANIMATE STAT NUMBERS ======
    const statNumbers = document.querySelectorAll('.animate-number');
    statNumbers.forEach(function (el) {
        const target = parseInt(el.textContent);
        animateNumber(el, 0, target, 800);
    });
});

// ====== NUMBER ANIMATION ======
function animateNumber(el, start, end, duration) {
    const range = end - start;
    const startTime = performance.now();
    function step(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.floor(start + range * eased);
        if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
}

// ====== CHART COLOR PALETTES ======
const chartColors = {
    backgrounds: [
        'rgba(108, 92, 231, 0.7)',
        'rgba(0, 206, 201, 0.7)',
        'rgba(253, 203, 110, 0.7)',
        'rgba(255, 118, 117, 0.7)',
        'rgba(116, 185, 255, 0.7)',
        'rgba(0, 184, 148, 0.7)',
        'rgba(162, 155, 254, 0.7)',
        'rgba(85, 239, 196, 0.7)',
    ],
    borders: [
        'rgba(108, 92, 231, 1)',
        'rgba(0, 206, 201, 1)',
        'rgba(253, 203, 110, 1)',
        'rgba(255, 118, 117, 1)',
        'rgba(116, 185, 255, 1)',
        'rgba(0, 184, 148, 1)',
        'rgba(162, 155, 254, 1)',
        'rgba(85, 239, 196, 1)',
    ],
};

// ====== Chart.js Defaults ======
if (typeof Chart !== 'undefined') {
    Chart.defaults.color = '#94A3B8';
    Chart.defaults.borderColor = 'rgba(255,255,255,0.05)';
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.padding = 16;
}

// ====== DASHBOARD CHARTS ======
function loadDashboardCharts() {
    // Category Chart
    fetch('/api/category-chart/')
        .then(r => r.json())
        .then(data => {
            new Chart(document.getElementById('categoryChart'), {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.values,
                        backgroundColor: chartColors.backgrounds,
                        borderColor: chartColors.borders,
                        borderWidth: 2,
                        hoverOffset: 8,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '65%',
                    plugins: {
                        legend: { position: 'bottom' },
                    },
                    animation: {
                        animateScale: true,
                        animateRotate: true,
                        duration: 1200,
                    }
                }
            });
        });

    // Stock Distribution Chart
    fetch('/api/stock-distribution/')
        .then(r => r.json())
        .then(data => {
            new Chart(document.getElementById('stockDistChart'), {
                type: 'pie',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.values,
                        backgroundColor: [
                            'rgba(0, 184, 148, 0.7)',
                            'rgba(253, 203, 110, 0.7)',
                            'rgba(255, 118, 117, 0.7)',
                        ],
                        borderColor: [
                            'rgba(0, 184, 148, 1)',
                            'rgba(253, 203, 110, 1)',
                            'rgba(255, 118, 117, 1)',
                        ],
                        borderWidth: 2,
                        hoverOffset: 8,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' },
                    },
                    animation: {
                        animateScale: true,
                        duration: 1200,
                    }
                }
            });
        });

    // Monthly Activity Chart
    fetch('/api/monthly-activity/')
        .then(r => r.json())
        .then(data => {
            new Chart(document.getElementById('monthlyChart'), {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Stock In',
                            data: data.stock_in,
                            backgroundColor: 'rgba(0, 184, 148, 0.6)',
                            borderColor: 'rgba(0, 184, 148, 1)',
                            borderWidth: 1,
                            borderRadius: 6,
                        },
                        {
                            label: 'Stock Out',
                            data: data.stock_out,
                            backgroundColor: 'rgba(255, 118, 117, 0.6)',
                            borderColor: 'rgba(255, 118, 117, 1)',
                            borderWidth: 1,
                            borderRadius: 6,
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top' },
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: 'rgba(255,255,255,0.04)' },
                        },
                        x: {
                            grid: { display: false },
                        }
                    },
                    animation: { duration: 1500 }
                }
            });
        });

    // Top Products Chart
    fetch('/api/top-products/')
        .then(r => r.json())
        .then(data => {
            new Chart(document.getElementById('topProductsChart'), {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Value (₹)',
                        data: data.values,
                        backgroundColor: chartColors.backgrounds,
                        borderColor: chartColors.borders,
                        borderWidth: 1,
                        borderRadius: 6,
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            grid: { color: 'rgba(255,255,255,0.04)' },
                        },
                        y: {
                            grid: { display: false },
                        }
                    },
                    animation: { duration: 1500 }
                }
            });
        });
}

// ====== REPORT CHARTS ======
function loadReportCharts() {
    fetch('/api/category-chart/')
        .then(r => r.json())
        .then(data => {
            new Chart(document.getElementById('reportCategoryChart'), {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.values,
                        backgroundColor: chartColors.backgrounds,
                        borderColor: chartColors.borders,
                        borderWidth: 2,
                        hoverOffset: 8,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '65%',
                    plugins: { legend: { position: 'bottom' } },
                    animation: { animateScale: true, duration: 1200 }
                }
            });
        });

    fetch('/api/stock-distribution/')
        .then(r => r.json())
        .then(data => {
            new Chart(document.getElementById('reportStockChart'), {
                type: 'pie',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.values,
                        backgroundColor: [
                            'rgba(0, 184, 148, 0.7)',
                            'rgba(253, 203, 110, 0.7)',
                            'rgba(255, 118, 117, 0.7)',
                        ],
                        borderColor: [
                            'rgba(0, 184, 148, 1)',
                            'rgba(253, 203, 110, 1)',
                            'rgba(255, 118, 117, 1)',
                        ],
                        borderWidth: 2,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } },
                    animation: { animateScale: true, duration: 1200 }
                }
            });
        });
}
