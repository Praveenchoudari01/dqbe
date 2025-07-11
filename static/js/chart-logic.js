const chartData = JSON.parse(document.getElementById('chart-data').textContent);

const ctx = document.getElementById('reportChart').getContext('2d');
const chartTypeMap = {
    'Bar Chart': 'bar',
    'Line Chart': 'line',
    'Pie Chart': 'pie',
    'Scatter Plot': 'scatter'
};

const chartType = chartTypeMap[chartData.graph_type] || 'bar';

new Chart(ctx, {
    type: chartType,
    data: {
        labels: chartData.labels,
        datasets: [{
            label: chartData.label,
            data: chartData.values,
            backgroundColor: [
                'rgba(255, 99, 132, 0.7)',
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 206, 86, 0.7)',
                'rgba(75, 192, 192, 0.7)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)'
            ],
            borderWidth: 2,
            borderRadius: 8,
            barPercentage: 0.7,
            categoryPercentage: 0.6
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                display: true,
                labels: {
                    color: '#333',
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                }
            },
            tooltip: {
                backgroundColor: '#f0f0f0',
                titleColor: '#333',
                bodyColor: '#333',
                borderColor: '#ccc',
                borderWidth: 1
            }
        },
        scales: {
            x: {
                ticks: {
                    color: '#333',
                    font: {
                        size: 12
                    }
                },
                grid: {
                    color: 'rgba(200,200,200,0.2)'
                }
            },
            y: {
                ticks: {
                    color: '#333',
                    font: {
                        size: 12
                    }
                },
                grid: {
                    color: 'rgba(200,200,200,0.2)'
                }
            }
        }
    }
});
