// ===== Element references =====
const checkAqiBtn = document.getElementById('check-aqi-btn');
const cityInput = document.getElementById('city-input');

const aqiLoading = document.getElementById('aqi-loading');
const aqiError = document.getElementById('aqi-error');
const aqiResult = document.getElementById('aqi-result');
const aqiNumber = document.getElementById('aqi-number');
const aqiCategory = document.getElementById('aqi-category');
const aqiCityLabel = document.getElementById('aqi-city-label');

const profileForm = document.getElementById('profile-form');
const profileNameInput = document.getElementById('profile-name');
const profileAgeGroupInput = document.getElementById('profile-age-group');
const healthConditionsFieldset = document.getElementById('health-conditions');
const advisorySubmitBtn = profileForm.querySelector('button[type="submit"]');

const advisorySection = document.getElementById('advisory-section');
const advisoryLoading = document.getElementById('advisory-loading');
const advisoryError = document.getElementById('advisory-error');
const advisoryResult = document.getElementById('advisory-result');

let currentAqiData = null;
let trendChart = null;


// ===== AQI check: loading / error / result state functions =====
function showAqiLoading() {
    aqiLoading.classList.remove('hidden');
    aqiError.classList.add('hidden');
    aqiResult.classList.add('hidden');

    checkAqiBtn.disabled = true;
    checkAqiBtn.textContent = 'Checking...';
}

function showAqiError(message) {
    aqiLoading.classList.add('hidden');
    aqiError.classList.remove('hidden');
    aqiError.classList.add('error-box');
    aqiResult.classList.add('hidden');

    checkAqiBtn.disabled = false;
    checkAqiBtn.textContent = 'Check AQI';

    aqiError.textContent = message;
}

function getAqiColorClass(category) {
    const map = {
        "Good": "aqi-good",
        "Moderate": "aqi-moderate",
        "Unhealthy for Sensitive Groups": "aqi-sensitive",
        "Unhealthy": "aqi-unhealthy",
        "Very Unhealthy": "aqi-very-unhealthy",
        "Hazardous": "aqi-hazardous"
    };
    return map[category] || "aqi-moderate";
}

const GLOW_COLORS = {
    "Good": "#00b34a",
    "Moderate": "#d4a600",
    "Unhealthy for Sensitive Groups": "#e07b00",
    "Unhealthy": "#d62828",
    "Very Unhealthy": "#7b2d8e",
    "Hazardous": "#6e001f"
};

function showAqiResult(data) {
    aqiLoading.classList.add('hidden');
    aqiError.classList.add('hidden');
    aqiResult.classList.remove('hidden');

    checkAqiBtn.disabled = false;
    checkAqiBtn.textContent = 'Check AQI';

    aqiNumber.textContent = data.aqi_us;
    aqiCategory.textContent = data.category;
    aqiCityLabel.textContent = `${data.city}, ${data.country}`;

    const badge = document.getElementById('aqi-badge');
    badge.className = '';
    badge.classList.add(getAqiColorClass(data.category));

    // Feed the live category color into the section (so both the breathing
    // glow AND the card's left-border accent inherit the same live color)
    document.getElementById('aqi-display').style.setProperty(
        '--glow-color',
        GLOW_COLORS[data.category] || "#235073"
    );
}


// ===== AQI check: fetch logic =====
async function fetchAqi(city) {
    showAqiLoading();

    try {
        const response = await fetch(`/api/aqi?city=${encodeURIComponent(city)}`);
        const data = await response.json();

        if (!response.ok) {
            showAqiError(data.error || 'Something went wrong fetching AQI data.');
            return;
        }

        currentAqiData = data;
        showAqiResult(data);
        loadTrendChart(data.city);

    } catch (err) {
        showAqiError('Could not reach the server. Is Flask running?');
        console.error(err);
    }
}

checkAqiBtn.addEventListener('click', () => {
    const city = cityInput.value.trim();
    if (!city) {
        showAqiError('Please enter a city name.');
        return;
    }
    fetchAqi(city);
});


// ===== Health profile / advisory: state functions =====
function getSelectedConditions() {
    const checkboxes = healthConditionsFieldset.querySelectorAll('input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

function showAdvisoryLoading() {
    advisorySection.classList.remove('hidden');
    advisoryLoading.classList.remove('hidden');
    advisoryError.classList.add('hidden');
    advisoryResult.classList.add('hidden');

    advisorySubmitBtn.disabled = true;
    advisorySubmitBtn.textContent = 'Getting advisory...';
}
function showAdvisoryError(message) {
    advisoryLoading.classList.add('hidden');
    advisoryError.classList.remove('hidden');
    advisoryError.classList.add('error-box');
    advisoryResult.classList.add('hidden');

    advisorySubmitBtn.disabled = false;
    advisorySubmitBtn.textContent = 'Get My Advisory';

    advisoryError.textContent = message;
}

function showAdvisoryResult(data) {
    advisoryLoading.classList.add('hidden');
    advisoryError.classList.add('hidden');
    advisoryResult.classList.remove('hidden');

    advisorySubmitBtn.disabled = false;
    advisorySubmitBtn.textContent = 'Get My Advisory';

    const risk = data.advisory.risk_score;
    const advisories = data.advisory.advisories;

    let html = `<p><strong>Current AQI in ${data.user.city}:</strong> ${data.current_aqi.aqi_us} (${data.current_aqi.category})</p>`;

    // Risk meter - 5 dots, filled up to the risk score
    html += `<div class="risk-meter"><span class="risk-meter-label">Risk for you</span><div class="risk-dots">`;
    for (let i = 1; i <= 5; i++) {
        html += `<span class="risk-dot${i <= risk ? ' filled' : ''}"></span>`;
    }
    html += `</div></div>`;

    html += '<ul>';
    advisories.forEach(a => {
        if (a.condition === 'none') {
            html += `<li>${a.advice}</li>`;
        } else {
            html += `<li><strong>${a.condition}:</strong> ${a.advice}</li>`;
        }
    });
    html += '</ul>';

    advisoryResult.innerHTML = html;
}

// ===== Multi-city comparison =====
const compareCityInput = document.getElementById('compare-city-input');
const addCompareBtn = document.getElementById('add-compare-btn');
const compareError = document.getElementById('compare-error');
const compareList = document.getElementById('compare-list');

let comparedCities = [];  // array of {city, aqi_us, category, country}

function renderCompareList() {
    compareList.innerHTML = '';

    comparedCities.forEach((entry, index) => {
        const card = document.createElement('div');
        card.className = 'compare-card';

        const numberSpan = document.createElement('span');
        numberSpan.className = `compare-card-number ${getAqiColorClass(entry.category)}`;
        numberSpan.textContent = entry.aqi_us;

        card.innerHTML = `
            <div>
                <div class="compare-card-city">${entry.city}, ${entry.country}</div>
                <div class="compare-card-meta">${entry.category}</div>
            </div>
        `;

        const readingWrap = document.createElement('div');
        readingWrap.className = 'compare-card-reading';
        readingWrap.appendChild(numberSpan);

        const removeBtn = document.createElement('button');
        removeBtn.className = 'compare-card-remove';
        removeBtn.textContent = '✕';
        removeBtn.addEventListener('click', () => {
            comparedCities.splice(index, 1);
            renderCompareList();
        });
        readingWrap.appendChild(removeBtn);

        card.appendChild(readingWrap);
        compareList.appendChild(card);
    });
}

async function addCityToCompare(city) {
    compareError.classList.add('hidden');
    addCompareBtn.disabled = true;
    addCompareBtn.textContent = '...';

    try {
        const response = await fetch(`/api/aqi?city=${encodeURIComponent(city)}`);
        const data = await response.json();

        if (!response.ok) {
            compareError.textContent = data.error || 'Could not fetch that city.';
            compareError.classList.remove('hidden');
            return;
        }

        // Avoid duplicate entries for the same city
        const alreadyAdded = comparedCities.some(c => c.city === data.city);
        if (alreadyAdded) {
            compareError.textContent = `${data.city} is already in your comparison.`;
            compareError.classList.remove('hidden');
            return;
        }

        comparedCities.push({
            city: data.city,
            country: data.country,
            aqi_us: data.aqi_us,
            category: data.category
        });
        renderCompareList();
        compareCityInput.value = '';

    } catch (err) {
        compareError.textContent = 'Could not reach the server.';
        compareError.classList.remove('hidden');
        console.error(err);
    } finally {
        addCompareBtn.disabled = false;
        addCompareBtn.textContent = 'Add';
    }
}

addCompareBtn.addEventListener('click', () => {
    const city = compareCityInput.value.trim();
    if (!city) return;
    addCityToCompare(city);
});

compareCityInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        addCompareBtn.click();
    }
});

// ===== Health profile / advisory: fetch logic =====
async function createUserAndGetAdvisory(name, ageGroup, conditions, city) {
    showAdvisoryLoading();

    try {
        const createResponse = await fetch('/api/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                age_group: ageGroup,
                health_conditions: conditions,
                city: city
            })
        });

        const createData = await createResponse.json();

        if (!createResponse.ok) {
            showAdvisoryError(createData.error || 'Could not create your profile.');
            return;
        }

        const advisoryResponse = await fetch(`/api/users/${createData.id}/advisory`);
        const advisoryData = await advisoryResponse.json();

        if (!advisoryResponse.ok) {
            showAdvisoryError(advisoryData.error || 'Could not fetch your advisory.');
            return;
        }

        showAdvisoryResult(advisoryData);

    } catch (err) {
        showAdvisoryError('Could not reach the server. Is Flask running?');
        console.error(err);
    }
}

profileForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const name = profileNameInput.value.trim();
    const ageGroup = profileAgeGroupInput.value;
    const conditions = getSelectedConditions();
    const city = cityInput.value.trim();

    if (!name || !ageGroup || !city) {
        showAdvisoryError('Please fill in your name, age group, and a city first.');
        return;
    }

    createUserAndGetAdvisory(name, ageGroup, conditions, city);
});


// ===== Trend chart =====
function getAqiChartColor(aqi) {
    if (aqi <= 50) return '#00e400';
    if (aqi <= 100) return '#ffff00';
    if (aqi <= 150) return '#ff7e00';
    if (aqi <= 200) return '#ff0000';
    if (aqi <= 300) return '#8f3f97';
    return '#7e0023';
}

async function loadTrendChart(city) {
    const emptyMsg = document.getElementById('trend-empty');
    const canvas = document.getElementById('trend-chart');

    try {
        const response = await fetch(`/api/history?city=${encodeURIComponent(city)}`);
        const data = await response.json();

        if (!response.ok || !data.readings || data.readings.length === 0) {
            emptyMsg.classList.remove('hidden');
            canvas.classList.add('hidden');
            return;
        }

        emptyMsg.classList.add('hidden');
        canvas.classList.remove('hidden');

        const labels = data.readings.map(r => {
            const date = new Date(r.recorded_at);
            return date.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric' });
        });
        const values = data.readings.map(r => r.aqi_us);
        const pointColors = values.map(v => getAqiChartColor(v));

        const ctx = canvas.getContext('2d');

        if (trendChart) {
            trendChart.destroy();
        }

        const chartFont = { family: "'IBM Plex Mono', monospace", size: 11 };

        trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'AQI (US)',
                    data: values,
                    borderColor: '#235073',
                    borderWidth: 2,
                    backgroundColor: 'rgba(35, 80, 115, 0.06)',
                    pointBackgroundColor: pointColors,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 1.5,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { labels: { font: chartFont, color: '#16233F' } }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'AQI (US)', font: chartFont, color: '#6E7A8F' },
                        ticks: { font: chartFont, color: '#6E7A8F' },
                        grid: { color: '#eef1f5' }
                    },
                    x: {
                        ticks: { font: chartFont, color: '#6E7A8F' },
                        grid: { display: false }
                    }
                }
            }
        });

    } catch (err) {
        console.error('Failed to load trend chart:', err);
        emptyMsg.classList.remove('hidden');
        emptyMsg.textContent = 'Could not load trend data right now.';
        canvas.classList.add('hidden');
    }
}


// ===== Initial load =====
fetchAqi(cityInput.value.trim());