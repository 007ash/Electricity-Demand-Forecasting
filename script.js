// script.js

async function fetchPrediction() {
    const startDate = document.getElementById("start-date").value;
    const startTime = document.getElementById("start-time").value;
    const endDate = document.getElementById("end-date").value;
    const endTime = document.getElementById("end-time").value;
    const outputText = document.getElementById("output-text");

    const data = {
        start_date: startDate,
        start_time: startTime,
        end_date: endDate,
        end_time: endTime
    };

    try {
        const response = await fetch('http://localhost:5000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const result = await response.json();
            const predictions = JSON.parse(result.result);
            
            // Displaying prediction results
            outputText.textContent = JSON.stringify(predictions, null, 2);

            // Plotting predictions on canvas (optional, using Chart.js)
            drawGraph(predictions);
        } else {
            outputText.textContent = "Error: Unable to fetch predictions.";
        }
    } catch (error) {
        outputText.textContent = "Error: " + error.message;
    }
}

// Function to draw the graph using Chart.js
function drawGraph(predictions) {
    const ctx = document.getElementById('graphCanvas').getContext('2d');
    const labels = predictions.map(item => item.hour);
    const data = predictions.map(item => item.pred);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Predicted Demand',
                data: data,
                borderColor: 'green',
                fill: false
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'Hour' }},
                y: { title: { display: true, text: 'Predicted Demand' }}
            }
        }
    });
}
