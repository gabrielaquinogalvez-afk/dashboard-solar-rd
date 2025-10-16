# ================================
# 🌞 Dashboard Solar RD (Render)
# ================================
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()

# --- Provincias de RD con coordenadas ---
PROVINCIAS = {
    "Santo Domingo": {"lat": 18.4861, "lon": -69.9312},
    "Santiago": {"lat": 19.4517, "lon": -70.6970},
    "La Vega": {"lat": 19.2220, "lon": -70.5280},
    "San Cristóbal": {"lat": 18.4160, "lon": -70.1090},
    "Puerto Plata": {"lat": 19.7934, "lon": -70.6884},
    "La Romana": {"lat": 18.4300, "lon": -68.9700},
    "San Pedro de Macorís": {"lat": 18.4500, "lon": -69.3000},
    "Barahona": {"lat": 18.2085, "lon": -71.1008},
    "Bonao": {"lat": 18.9395, "lon": -70.4095},
    "Higüey": {"lat": 18.6167, "lon": -68.7000}
}

# --- HTML del Dashboard ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>🌞 Dashboard Solar RD</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.0"></script>
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }
        h1 { text-align: center; color: #1b4d89; }
        select { padding: 8px; margin: 10px; font-size: 16px; }
        canvas { background: white; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }
        .info-box { text-align: center; margin-top: 20px; font-size: 18px; background: #e0f7fa; padding: 10px; border-radius: 8px; }
    </style>
</head>
<body>
    <h1>☀️ Producción Solar - República Dominicana</h1>
    <div style="text-align:center;">
        <label for="provincia">Selecciona una provincia:</label>
        <select id="provincia" onchange="loadRadiation()">
            {options}
        </select>
    </div>
    <canvas id="radiationChart" width="800" height="400"></canvas>
    <div class="info-box" id="infoBox">Selecciona una provincia para ver la información.</div>

    <script>
        const ctx = document.getElementById('radiationChart').getContext('2d');
        let chart;

        async function loadRadiation() {
            const provincia = document.getElementById('provincia').value;
            const response = await fetch(`/radiation?provincia=${provincia}`);
            const data = await response.json();

            const labels = data.hours;
            const values = data.values;
            const info = data.info;

            document.getElementById('infoBox').innerHTML = `
                ☀️ Provincia: <b>${provincia}</b><br>
                📅 Fecha: ${info.date}<br>
                🌤️ Radiación máxima: ${info.max} W/m²<br>
                🌅 Radiación promedio: ${info.avg} W/m²
            `;

            if (chart) chart.destroy();

            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Radiación Solar (W/m²)',
                        data: values,
                        borderColor: '#1b4d89',
                        backgroundColor: 'rgba(27, 77, 137, 0.2)',
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        zoom: {
                            pan: { enabled: true, mode: 'x', modifierKey: 'ctrl' },
                            zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: 'x' }
                        }
                    },
                    scales: {
                        y: { beginAtZero: true },
                        x: { title: { display: true, text: 'Hora del día' } }
                    }
                }
            });
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    options = "".join([f"<option value='{prov}'>{prov}</option>" for prov in PROVINCIAS.keys()])
    return HTML_TEMPLATE.format(options=options)

@app.get("/radiation")
async def get_radiation(provincia: str):
    if provincia not in PROVINCIAS:
        return {"error": "Provincia no válida"}
    lat = PROVINCIAS[provincia]["lat"]
    lon = PROVINCIAS[provincia]["lon"]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=shortwave_radiation&timezone=America%2FSanto_Domingo"
    r = requests.get(url).json()
    hours = r["hourly"]["time"]
    values = r["hourly"]["shortwave_radiation"]

    max_rad = max(values)
    avg_rad = round(sum(values)/len(values), 2)
    date = hours[0].split("T")[0]

    return {
        "hours": [h.split("T")[1] for h in hours],
        "values": values,
        "info": {"max": max_rad, "avg": avg_rad, "date": date}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
