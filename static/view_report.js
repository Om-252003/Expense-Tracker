document.addEventListener('DOMContentLoaded', function () {
    const lazyLoadObserver = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const canvas = entry.target;
                    if (!canvas.classList.contains('visible')) {
                        canvas.classList.add('visible');
                        loadChart(canvas.id);
                    }
                }
            });
        },
        { threshold: 0.5 }
    );

    const canvases = document.querySelectorAll('canvas');
    canvases.forEach((canvas) => lazyLoadObserver.observe(canvas));

    function loadChart(canvasId) {
        if (canvasId === 'barChart') {
            const barChartCtx = document.getElementById('barChart').getContext('2d');
            new Chart(barChartCtx, {
                type: 'bar',
                data: {
                    labels: JSON.parse(bar_chart_labels),
                    datasets: [{
                        label: 'Net Transaction Amount',
                        data: JSON.parse(bar_chart_values).map(value => Math.abs(value)),
                        backgroundColor: (context) => context.raw >= 0 ? 'rgba(75, 192, 192, 0.6)' : 'rgba(255, 99, 132, 0.6)',
                        borderColor: (context) => context.raw >= 0 ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: true, position: 'top' },
                        datalabels: {
                            anchor: 'end',
                            align: 'top',
                            formatter: (value) => `$${Math.abs(value)}`, // Ensure value above bar is positive
                            font: { size: 14, weight: 'bold' },
                            color: '#333'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: { display: true, text: 'Amount' }
                        },
                        x: {
                            title: { display: true, text: 'Date' }
                        }
                    }
                },
                plugins: [ChartDataLabels]
            });
        } else if (canvasId === 'pieChart') {
            const pieChartCtx = document.getElementById('pieChart').getContext('2d');
            new Chart(pieChartCtx, {
                type: 'pie',
                data: {
                    labels: ['Income', 'Expense'],
                    datasets: [{
                        data: JSON.parse(pie_chart_data).map(value => Math.abs(value)), // Absolute values for pie data
                        backgroundColor: ['rgba(75, 192, 192, 0.6)', 'rgba(255, 99, 132, 0.6)'],
                        borderColor: ['rgba(75, 192, 192, 1)', 'rgba(255, 99, 132, 1)'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' },
                        datalabels: {
                            formatter: (value, context) => `$${value}`, // Display positive value
                            font: { size: 14, weight: 'bold' },
                            color: '#fff'
                        }
                    }
                },
                plugins: [ChartDataLabels]
            });
        }
    }
});
