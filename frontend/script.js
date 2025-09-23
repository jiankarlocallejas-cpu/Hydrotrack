// I luv cats ❤ Signed - Jian in 09/17/25
const form = document.getElementById('waterForm');
const resultDiv = document.getElementById('result');
const predictionText = document.getElementById('predictionText');

const API_URL = "https://hydrotrack-b3u4.onrender.com/predict";

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const formData = new FormData(form);
  const data = {
    household_size: Number(formData.get('household_size')),
    appliances: Number(formData.get('appliances')),
    outdoor_use: Number(formData.get('outdoor_use')),
    daily_reading: Number(formData.get('daily_reading'))
  };

  predictionText.textContent = "Calculating...";
  resultDiv.classList.remove('hidden');

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    });

    if (!response.ok) throw new Error(`Server error: ${response.status}`);

    const result = await response.json();
    predictionText.textContent = `Estimated Monthly Water Consumption: ${result.prediction} liters`;
  } catch (err) {
    predictionText.textContent = `Error: ${err.message}`;
  }
});
