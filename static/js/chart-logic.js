// 1. CHART RENDERING LOGIC
document.addEventListener("DOMContentLoaded", function () {
    const chartDataScript = document.getElementById('chart-data');
    if (chartDataScript) {
        const chartData = JSON.parse(chartDataScript.textContent);
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
                            font: { size: 14, weight: 'bold' }
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
                            font: { size: 12 }
                        },
                        grid: { color: 'rgba(200,200,200,0.2)' }
                    },
                    y: {
                        ticks: {
                            color: '#333',
                            font: { size: 12 }
                        },
                        grid: { color: 'rgba(200,200,200,0.2)' }
                    }
                }
            }
        });
    }

    // 2. DYNAMIC FIELD & SORT OPTIONS LOGIC
    const attributes = window.availableAttributes || {};
    const table1Select = document.getElementById('table1');
    const table2Select = document.getElementById('table2');
    const fieldContainer = document.getElementById('field-container');
    const sortFieldSelect = document.getElementById('sort_field');

    function updateFields() {
        const table1 = table1Select.value;
        const table2 = table2Select.value;

        const fields1 = attributes[table1] || [];
        const fields2 = attributes[table2] || [];
        const allFields = [...new Set([...fields1, ...fields2])];

        // Clear old fields
        fieldContainer.innerHTML = '';
        sortFieldSelect.innerHTML = '<option value="">-- No Sorting --</option>';

        // Add new fields
        allFields.forEach(field => {
            // Field checkbox
            const label = document.createElement('label');
            label.innerHTML = `<input type="checkbox" name="fields" value="${field}"> ${field}`;
            fieldContainer.appendChild(label);
            fieldContainer.appendChild(document.createElement('br'));

            // Sort option
            const option = document.createElement('option');
            option.value = field;
            option.textContent = field;
            sortFieldSelect.appendChild(option);
        });
    }

    if (table1Select && table2Select) {
        table1Select.addEventListener('change', updateFields);
        table2Select.addEventListener('change', updateFields);
        updateFields(); // Initial load
    }
});
