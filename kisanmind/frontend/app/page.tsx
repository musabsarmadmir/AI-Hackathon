/* app/page.tsx */
"use client";

import { useState } from "react";
import axios from "axios";
import Image from "next/image";

interface DiagnosisResult {
  disease: string;
  confidence: number;
}

interface WeatherResult {
  schedule: { day: number; water_liters: number }[];
}

interface TreatmentResult {
  organic: string;
  chemical: string;
}

interface SupplierResult {
  suppliers: { name: string; address: string; distance_km: number }[];
}

export default function Home() {
  const [imageUrl, setImageUrl] = useState<string>("");
  const [location, setLocation] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [diagnosis, setDiagnosis] = useState<DiagnosisResult | null>(null);
  const [weather, setWeather] = useState<WeatherResult | null>(null);
  const [treatment, setTreatment] = useState<TreatmentResult | null>(null);
  const [suppliers, setSuppliers] = useState<SupplierResult | null>(null);

  const handleSubmit = async () => {
    if (!imageUrl) return alert("Please provide an image URL first.");
    setLoading(true);
    try {
      const base = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

      // 1️⃣ Diagnose the crop
      const diagRes = await axios.post(`${base}/diagnose`, { image_url: imageUrl, location });
      const diagData: DiagnosisResult = diagRes.data;
      setDiagnosis(diagData);

      // 2️⃣ Weather advisory (pass location)
      const weatherRes = await axios.post(`${base}/weather`, { location });
      const weatherData: WeatherResult = weatherRes.data;
      setWeather(weatherData);

      // 3️⃣ Treatment based on diagnosis
      const treatRes = await axios.post(`${base}/treatment`, { crop: "wheat", disease: diagData.disease });
      const treatData: TreatmentResult = treatRes.data;
      setTreatment(treatData);

      // 4️⃣ Supplier lookup
      const suppRes = await axios.post(`${base}/supplier`, { crop: "wheat", location, need: treatData.chemical });
      const suppData: SupplierResult = suppRes.data;
      setSuppliers(suppData);
    } catch (e) {
      console.error(e);
      alert("Something went wrong – check console for details.");
    } finally {
      setLoading(false);
    }
  };

  // For privacy and removing demo keys, accept an image URL from the user instead of uploading.
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    // keep existing handler name but prompt for a URL; no third-party demo keys used.
    const url = prompt("Paste a public image URL for your crop photo:");
    if (url) setImageUrl(url);
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-green-50 to-blue-100 p-6">
      <h1 className="text-4xl font-bold mb-6 text-green-800 drop-shadow-md">KisanMind 🌾</h1>
      <div className="w-full max-w-md bg-white rounded-xl shadow-lg p-6 mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Crop photo URL</label>
        <div className="flex gap-2">
          <input type="text" placeholder="https://example.com/mycrop.jpg" value={imageUrl} onChange={e => setImageUrl(e.target.value)} className="w-full rounded border-gray-300 focus:border-green-500 focus:ring-green-500" />
          <button onClick={handleFileChange} className="px-3 py-1 bg-gray-100 rounded">Paste URL</button>
        </div>
        {imageUrl && (
          <div className="mt-4 relative h-48">
            <Image src={imageUrl} alt="Crop" fill style={{ objectFit: "contain" }} />
          </div>
        )}
        <label className="block text-sm font-medium text-gray-700 mt-4 mb-2">Location (city)</label>
        <input type="text" placeholder="e.g. Lahore" value={location} onChange={e => setLocation(e.target.value)} className="w-full rounded border-gray-300 focus:border-green-500 focus:ring-green-500" />
        <button onClick={handleSubmit} disabled={loading} className="mt-4 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition">
          {loading ? "Processing…" : "Run KisanMind"}
        </button>
      </div>

      {/* Results cards */}
      <div className="grid gap-4 w-full max-w-2xl">
        {diagnosis && (
          <section className="bg-green-50 p-4 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-2 text-green-800">🦠 Diagnosis</h2>
            <p><strong>Disease:</strong> {diagnosis.disease}</p>
            <p><strong>Confidence:</strong> {(diagnosis.confidence * 100).toFixed(0)}%</p>
          </section>
        )}
        {weather && (
          <section className="bg-blue-50 p-4 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-2 text-blue-800">🌧️ Weather & Irrigation</h2>
            <ul className="list-disc pl-5 space-y-1">
              {weather.schedule.map(d => (
                <li key={d.day}>Day {d.day}: {d.water_liters} L water</li>
              ))}
            </ul>
          </section>
        )}
        {treatment && (
          <section className="bg-yellow-50 p-4 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-2 text-yellow-800">💊 Treatment Options</h2>
            <p><strong>Organic:</strong> {treatment.organic}</p>
            <p><strong>Chemical:</strong> {treatment.chemical}</p>
          </section>
        )}
        {suppliers && (
          <section className="bg-purple-50 p-4 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-2 text-purple-800">📍 Nearby Suppliers</h2>
            <ul className="list-none space-y-2">
              {suppliers.suppliers.map((s, i) => (
                <li key={i} className="border-b pb-2">
                  <p className="font-medium">{s.name} ({s.distance_km} km)</p>
                  <p className="text-sm text-gray-600">{s.address}</p>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </main>
  );
}
