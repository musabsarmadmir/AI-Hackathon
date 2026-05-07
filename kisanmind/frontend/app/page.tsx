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
    if (!imageUrl) return alert("Please upload a photo first.");
    setLoading(true);
    try {
      // 1️⃣ Diagnose the crop
      const diagRes = await axios.post("/api/diagnose", { image_url: imageUrl, location });
      const diagData: DiagnosisResult = JSON.parse(diagRes.data);
      setDiagnosis(diagData);

      // 2️⃣ Weather advisory (pass location)
      const weatherRes = await axios.post("/api/weather", { location });
      const weatherData: WeatherResult = JSON.parse(weatherRes.data);
      setWeather(weatherData);

      // 3️⃣ Treatment based on diagnosis
      const treatRes = await axios.post("/api/treatment", { crop: "wheat", disease: diagData.disease });
      const treatData: TreatmentResult = JSON.parse(treatRes.data);
      setTreatment(treatData);

      // 4️⃣ Supplier lookup
      const suppRes = await axios.post("/api/supplier", { crop: "wheat", location, need: treatData.chemical });
      const suppData: SupplierResult = JSON.parse(suppRes.data);
      setSuppliers(suppData);
    } catch (e) {
      console.error(e);
      alert("Something went wrong – check console for details.");
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    // Simple client‑side upload to imgbb (public demo key) – replace with your own storage in prod.
    const form = new FormData();
    form.append("image", file);
    const res = await fetch("https://api.imgbb.com/1/upload?key=1c2a3b4c5d6e7f8g9h0i", { method: "POST", body: form });
    const json = await res.json();
    setImageUrl(json.data.url);
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-green-50 to-blue-100 p-6">
      <h1 className="text-4xl font-bold mb-6 text-green-800 drop-shadow-md">KisanMind 🌾</h1>
      <div className="w-full max-w-md bg-white rounded-xl shadow-lg p-6 mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Upload crop photo</label>
        <input type="file" accept="image/*" onChange={handleFileChange} className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-600 file:text-white hover:file:bg-green-700" />
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
