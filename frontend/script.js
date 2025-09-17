const API_URL = "http://localhost:5000"; // change to Render backend URL when deployed

const form = document.getElementById("predict-form");
const result = document.getElementById("result");

let chartCtx = document.getElementById("chart").getContext("2d");
let predictionChart = new Chart(chartCtx, {
  type: "line",
  data: {
    labels: [],
    datasets: [{
      label: "Predicted Water Consumption",
      data: [],
      borderColor: "#0077cc",
      fill: false
    }]
  }
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const household_size = document.getElementById("household_size").value;
  const income = document.getElementById("income").value;
  const lot_area = document.getElementById("lot_area").value;

  const response = await fetch(`${API_URL}/predict`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({household_size, income, lot_area})
  });
  const data = await response.json();

  result.textContent = `Predicted Consumption: ${data.prediction.toFixed(2)} units`;

  // Update chart
  predictionChart.data.labels.push(`Entry ${predictionChart.data.labels.length+1}`);
  predictionChart.data.datasets[0].data.push(data.prediction);
  predictionChart.update();
});
