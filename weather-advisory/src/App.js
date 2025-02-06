import React, { useState } from "react";
import axios from "axios";

function App() {
    const [city, setCity] = useState("");
    const [weather, setWeather] = useState(null);
    const [recommendation, setRecommendation] = useState(null);

    const handleGetWeather = async () => {
      if (!city) return;
      try {
          const response = await axios.post(
              "http://127.0.0.1:8000/get_weather",
              { city },
              {
                  headers: {
                      "Content-Type": "application/json",
                  },
              }
          );
          setWeather(response.data.weather_info);
          setRecommendation(response.data.recommendation);
      } catch (error) {
          console.error("Error fetching weather:", error);
      }
  };
  

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
            <h1 className="text-2xl font-bold mb-4">Weather Advisory</h1>
            <input
                type="text"
                placeholder="Enter city..."
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="p-2 border rounded"
            />
            <button onClick={handleGetWeather} className="mt-2 p-2 bg-blue-500 text-white rounded">
                Get Weather & Advice
            </button>
            {weather && (
                <div className="mt-4 p-4 bg-white shadow rounded text-center">
                    <p><strong>Weather:</strong> {weather}</p>
                    <p><strong>Advice:</strong> {recommendation}</p>
                </div>
            )}
        </div>
    );
}

export default App;
