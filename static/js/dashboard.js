/**
 * Dashboard Analytics & Charts
 * Utilizes Chart.js with dynamic data fetched from /api/dashboard-charts
 */

document.addEventListener('DOMContentLoaded', function () {
    const chartColors = [
        '#2563eb', '#10b981', '#f59e0b', '#ef4444', 
        '#06b6d4', '#8b5cf6', '#ec4899', '#64748b'
    ];

    fetch('/api/dashboard-charts')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            renderCategoryChart(data.categories);
            renderStatusChart(data.statuses);
            renderConditionChart(data.conditions);
            renderValueChart(data.values_by_category);
        })
        .catch(error => {
            console.error('Error fetching dashboard chart data:', error);
        });

    function renderCategoryChart(catData) {
        const ctx = document.getElementById('categoryChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: catData.labels.length ? catData.labels : ['No Categories'],
                datasets: [{
                    data: catData.values.length ? catData.values : [0],
                    backgroundColor: chartColors,
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { boxWidth: 12, padding: 15, font: { family: 'Inter', size: 11 } }
                    }
                },
                cutout: '65%'
            }
        });
    }

    function renderStatusChart(statusData) {
        const ctx = document.getElementById('statusChart');
        if (!ctx) return;

        const statusColorMap = {
            'Available': '#10b981',
            'Assigned': '#2563eb',
            'Under Maintenance': '#f59e0b',
            'Lost': '#ef4444',
            'Retired': '#64748b',
            'Disposed': '#1e293b'
        };

        const bgColors = statusData.labels.map(l => statusColorMap[l] || '#94a3b8');

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: statusData.labels.length ? statusData.labels : ['No Status Data'],
                datasets: [{
                    data: statusData.values.length ? statusData.values : [0],
                    backgroundColor: bgColors,
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { boxWidth: 12, padding: 15, font: { family: 'Inter', size: 11 } }
                    }
                }
            }
        });
    }

    function renderConditionChart(condData) {
        const ctx = document.getElementById('conditionChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: condData.labels.length ? condData.labels : ['No Conditions'],
                datasets: [{
                    label: 'Number of Assets',
                    data: condData.values.length ? condData.values : [0],
                    backgroundColor: '#3b82f6',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1, precision: 0 }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }

    function renderValueChart(valData) {
        const ctx = document.getElementById('valueChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: valData.labels.length ? valData.labels : ['No Value Data'],
                datasets: [{
                    label: 'Asset Value ($)',
                    data: valData.values.length ? valData.values : [0],
                    backgroundColor: '#10b981',
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return ' Value: $' + Number(context.parsed.x).toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            callback: function (val) {
                                return '$' + Number(val).toLocaleString();
                            }
                        }
                    },
                    y: {
                        grid: { display: false }
                    }
                }
            }
        });
    }
});

