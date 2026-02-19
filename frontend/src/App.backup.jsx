import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { Line, Bar } from 'react-chartjs-2';
import {
  Search,
  Map as MapIcon,
  Activity,
  Wind,
  Droplets,
  Flame,
  TreeDeciduous,
  Thermometer,
  Lightbulb,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  Users
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

// Register ChartJS
ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler
);

// --- COMPREHENSIVE MOCK DB (All 6 Species) ---
const MOCK_DB = {
  "Bengal Tiger": {
    name: "Bengal Tiger",
    status: "Endangered",
    location: { lat: 21.0, lon: 79.0, zoom: 6 },
    checkpoints: [
      { lat: 21.1, lon: 79.2, conf: 0.98 },
      { lat: 20.8, lon: 78.9, conf: 0.95 },
      { lat: 21.5, lon: 79.5, conf: 0.92 },
    ],
    population: [2200, 2250, 2300, 2350, 2400], // Rising
    years: ['2020', '2021', '2022', '2023', '2024'],
    analysis: {
      vegetation: { ndvi: [0.72, 0.70, 0.68, 0.65, 0.62], evi: [0.55, 0.53, 0.50, 0.48, 0.45] },
      climate: { temp: [28.1, 28.3, 28.6, 28.9, 29.2], rain: [1200, 1150, 1100, 1050, 1000] },
      disturbance: { frp: [12, 15, 22, 18, 35], nightlight: [2, 3, 5, 8, 12] }
    },
    advice: [
      "Increase patrol frequency in Northern corridor due to rising fire risks.",
      "Deploy water holes in Sector 4; rainfall declining by 15%.",
      "Limit road construction; night-light data shows habitat encroachment."
    ]
  },
  "Syzygium travancoricum": {
    name: "Syzygium travancoricum",
    status: "Critically Endangered",
    location: { lat: 10.0, lon: 76.5, zoom: 8 },
    checkpoints: [
      { lat: 9.8, lon: 76.4, conf: 0.99 },
      { lat: 10.1, lon: 76.6, conf: 0.85 },
    ],
    population: [120, 115, 110, 105, 100], // Declining
    years: ['2020', '2021', '2022', '2023', '2024'],
    analysis: {
      vegetation: { ndvi: [0.85, 0.84, 0.83, 0.82, 0.81], evi: [0.70, 0.69, 0.68, 0.68, 0.67] },
      climate: { temp: [24.0, 24.1, 24.2, 24.3, 24.4], rain: [2500, 2480, 2450, 2400, 2350] },
      disturbance: { frp: [0, 0, 2, 1, 0], nightlight: [10, 12, 15, 18, 20] }
    },
    advice: [
      "Strictly protect remaining swamp patches; urbanization is encroaching.",
      "Monitor groundwater levels; highly sensitive to drought.",
      "Engage local farmers to prevent wetland drainage."
    ]
  },
  "Semecarpus kathalekanensis": {
    name: "Semecarpus kathalekanensis",
    status: "Endangered",
    location: { lat: 14.0, lon: 74.5, zoom: 8 },
    checkpoints: [{ lat: 14.1, lon: 74.6, conf: 0.90 }],
    population: [450, 440, 445, 450, 455], // Stable
    years: ['2020', '2021', '2022', '2023', '2024'],
    analysis: {
      vegetation: { ndvi: [0.78, 0.79, 0.78, 0.78, 0.79], evi: [0.60, 0.61, 0.60, 0.60, 0.61] },
      climate: { temp: [26.0, 26.1, 26.0, 26.2, 26.3], rain: [2000, 2100, 2050, 2000, 1950] },
      disturbance: { frp: [5, 4, 6, 5, 4], nightlight: [5, 5, 6, 6, 7] }
    },
    advice: [
      "Maintain current protection status; population appears stable.",
      "Conduct annual surveys to detect early signs of fungal disease.",
      "Seed banking initiative recommended."
    ]
  },
  "Hopea parviflora": {
    name: "Hopea parviflora",
    status: "Endangered",
    location: { lat: 12.0, lon: 75.5, zoom: 7 },
    checkpoints: [{ lat: 12.1, lon: 75.6, conf: 0.88 }, { lat: 11.9, lon: 75.4, conf: 0.92 }],
    population: [800, 780, 760, 750, 740], // Moderate Decline
    years: ['2020', '2021', '2022', '2023', '2024'],
    analysis: {
      vegetation: { ndvi: [0.65, 0.64, 0.63, 0.62, 0.61], evi: [0.50, 0.49, 0.48, 0.47, 0.46] },
      climate: { temp: [27.0, 27.2, 27.4, 27.6, 27.8], rain: [1800, 1750, 1700, 1650, 1600] },
      disturbance: { frp: [10, 12, 15, 14, 16], nightlight: [8, 9, 10, 11, 12] }
    },
    advice: [
      "Restrict timber harvesting in buffer zones.",
      "Address invasive weed proliferation in fragmented areas.",
      "Community awareness program on value of old-growth trees."
    ]
  },
  "Diospyros nilagirica": {
    name: "Diospyros nilagirica",
    status: "Critically Endangered",
    location: { lat: 11.5, lon: 76.5, zoom: 9 }, // Nilgiris
    checkpoints: [{ lat: 11.4, lon: 76.6, conf: 0.95 }],
    population: [50, 48, 45, 42, 40], // Sharp Decline
    years: ['2020', '2021', '2022', '2023', '2024'],
    analysis: {
      vegetation: { ndvi: [0.60, 0.58, 0.55, 0.53, 0.50], evi: [0.45, 0.43, 0.40, 0.38, 0.35] },
      climate: { temp: [18.0, 18.2, 18.5, 18.8, 19.0], rain: [1500, 1450, 1400, 1350, 1300] },
      disturbance: { frp: [2, 3, 5, 8, 10], nightlight: [15, 16, 18, 19, 21] }
    },
    advice: [
      "Immediate ex-situ conservation (create botanical garden backup).",
      "Investigate tea plantation expansion into core habitat.",
      "Strict anti-poaching measures."
    ]
  },
  "Myristica malabarica": {
    name: "Myristica malabarica",
    status: "Endangered",
    location: { lat: 13.5, lon: 75.0, zoom: 8 },
    checkpoints: [{ lat: 13.4, lon: 74.9, conf: 0.89 }],
    population: [300, 290, 285, 280, 275], // Slow Decline
    years: ['2020', '2021', '2022', '2023', '2024'],
    analysis: {
      vegetation: { ndvi: [0.80, 0.79, 0.78, 0.78, 0.77], evi: [0.65, 0.64, 0.63, 0.63, 0.62] },
      climate: { temp: [25.0, 25.1, 25.2, 25.3, 25.4], rain: [2200, 2180, 2160, 2140, 2120] },
      disturbance: { frp: [1, 1, 2, 1, 2], nightlight: [6, 7, 8, 9, 10] }
    },
    advice: [
      "Map and protect all freshwater swamps in the district.",
      "Regulate upstream water diversion projects.",
      "Research into pollination biology required."
    ]
  }
};

// Map Updater Component
function MapUpdater({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, zoom, { duration: 1.5 });
  }, [center, zoom, map]);
  return null;
}

function App() {
  // --- STATE ---
  console.log('App: Rendering. activeSpecies:', activeSpecies, 'loading:', loading, 'error:', error);
  const [speciesName, setSpeciesName] = useState('Tiger');
  const [activeSpecies, setActiveSpecies] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // --- API FETCH ---
  const loadSpecies = async (paramName) => {
    setLoading(true);
    setError(null);
    try {
      console.log('App: Fetching', paramName);
      // Query our Unified API
      const response = await fetch(`http://localhost:8000/api/v1/species/${paramName}`);
      console.log('App: Response received', response.status, response.ok);
      if (!response.ok) {
        throw new Error('Species not found in database or GBIF network.');
      }
      const data = await response.json();

      // Data Transformation for UI
      // Calculate center from checkpoints if available
      let center = [20, 78]; // Default Center
      if (data.checkpoints && data.checkpoints.length > 0) {
        const lats = data.checkpoints.map(c => c.lat);
        const lons = data.checkpoints.map(c => c.lon);
        const avgLat = lats.reduce((a, b) => a + b, 0) / lats.length;
        const avgLon = lons.reduce((a, b) => a + b, 0) / lons.length;
        center = [avgLat, avgLon];
      } else if (data.checkpoints_region) {
        // Fallback to region box center
        center = [
          (data.checkpoints_region.lat_min + data.checkpoints_region.lat_max) / 2,
          (data.checkpoints_region.lon_min + data.checkpoints_region.lon_max) / 2
        ];
      }

      const uiData = {
        id: paramName, // Keep query param
        name: data.species_name, // Use Official/Corrected Name
        status: data.status,
        population: data.population_history,
        location: center, // Dynamic real locations
        description: `Real-time data fetched for ${data.species_name}.`,
        stats: {
          ndvi: data.ideal_env?.ndvi ?? 0.5,
          temp: data.ideal_env?.temp ?? 25
        },
        advice: [], // Will be filled by analysis
        checkpoints: data.checkpoints,
        sensitivities: data.sensitivities
      };

      setActiveSpecies(uiData);
      setSpeciesName(data.species_name); // Auto-update input to correct spelling
    } catch (err) {
      console.error('App: Error loading species', err);
      setError(err.message);
      setActiveSpecies(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (speciesName) {
      loadSpecies(speciesName.trim());
    }
  };

  // Initial Load
  useEffect(() => {
    loadSpecies('Bengal Tiger');
  }, []);


  // --- CHART CONFIGS ---
  const popOptions = {
    responsive: true,
    plugins: { legend: { display: false }, title: { display: true, text: 'Population History (Last 5 Years)' } },
    scales: { y: { beginAtZero: false } }
  };

  const vegOptions = {
    responsive: true,
    plugins: { legend: { position: 'bottom' }, title: { display: true, text: 'Vegetation Health (NDVI/EVI)' } },
    scales: { y: { beginAtZero: false } }
  };

  const climateOptions = {
    responsive: true,
    plugins: { legend: { position: 'bottom' }, title: { display: true, text: 'Climate Forecast (CMIP6)' } },
  };

  const disturbOptions = {
    responsive: true,
    plugins: { legend: { position: 'bottom' }, title: { display: true, text: 'Human & Fire Disturbance' } },
  };


  // --- RISK ANALYSIS (EcoGuard Engine) ---
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  const runZoneAnalysis = async () => {
    setAnalyzing(true);
    try {
      // Mock H3 index for demo
      const h3Index = "8928308280fffff";
      const res = await axios.get(`http://localhost:8000/api/v1/analytics/prescriptions/${h3Index}?species=${activeSpecies.name}`);
      setAnalysisResult(res.data);
    } catch (err) {
      console.error("Analysis Failed", err);
      alert("Failed to run EcoGuard engine.");
    } finally {
      setAnalyzing(false);
    }
  };

  // --- LOADING / ERROR STATES ---
  if (loading && !activeSpecies) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-emerald-200 border-t-emerald-600 rounded-full animate-spin mx-auto mb-4"></div>
          <h2 className="text-xl font-bold text-slate-700">Loading WildSight...</h2>
          <p className="text-slate-500">Connecting to global biodiversity network</p>
        </div>
      </div>
    );
  }

  if (error && !activeSpecies) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center max-w-md p-8 bg-white rounded-2xl shadow-xl">
          <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-slate-800 mb-2">Connection Failed</h2>
          <p className="text-slate-600 mb-6">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  // Safety fallback if activeSpecies is still null (shouldn't happen with loading/error guards but good practice)
  if (!activeSpecies) {
    console.warn('App: activeSpecies is null, returning Fallback UI');
    return <div className="p-10 font-bold text-xl">Waiting for initial data... (Check console)</div>;
  }

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-800 pb-10 relative">

      {/* ANALYSIS MODAL OVERLAY */}
      {analysisResult && (
        <div className="fixed inset-0 z-[999] bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-indigo-900 text-white rounded-t-2xl">
              <div>
                <h3 className="text-xl font-bold flex items-center gap-2">
                  <Lightbulb className="text-yellow-400" />
                  EcoGuard Prescriptive Engine
                </h3>
                <p className="text-indigo-200 text-sm">Zone ID: {analysisResult.zone}</p>
              </div>
              <button onClick={() => setAnalysisResult(null)} className="p-2 hover:bg-indigo-800 rounded-full transition-colors">
                ✕
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Risk Section */}
              <div className="flex gap-4 p-4 bg-orange-50 rounded-xl border border-orange-100">
                <AlertTriangle className="text-orange-600 shrink-0" />
                <div>
                  <h4 className="font-bold text-orange-900">Risk Assessment: {(analysisResult.risk_assessment.risk_score * 100).toFixed(0)}/100</h4>
                  <p className="text-orange-800 text-sm">Primary Stressor: <span className="uppercase font-bold">{analysisResult.risk_assessment.primary_stressor}</span></p>
                </div>
              </div>

              {/* Actions List */}
              <div>
                <h4 className="font-bold text-slate-800 mb-4 flex items-center gap-2"><ShieldCheck size={18} className="text-emerald-600" /> Recommended Interventions</h4>
                <div className="space-y-3">
                  {analysisResult.recommended_actions.map((action, i) => (
                    <div key={i} className="border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-2">
                        <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${action.priority === 'critical' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>
                          {action.priority} Priority
                        </span>
                        <span className="text-sm font-bold text-slate-500">${action.estimated_cost.toLocaleString()}</span>
                      </div>
                      <h5 className="font-bold text-slate-900">{action.action_type.replace('_', ' ').toUpperCase()}</h5>

                      {/* Description with Line Break Support */}
                      <div className="text-slate-600 text-sm mt-3 whitespace-pre-wrap leading-relaxed">
                        {action.description.split('\n').map((line, idx) => {
                          // Simple Bold Logic for steps
                          if (line.trim().startsWith('###') || line.trim().startsWith('**')) {
                            return <p key={idx} className="font-bold text-slate-800 mb-1">{line.replace(/###/g, '').replace(/\*\*/g, '')}</p>;
                          }
                          return <span key={idx}>{line}<br /></span>;
                        })}
                      </div>

                      {/* Enhanced Outcome Box */}
                      <div className="mt-4 p-3 bg-emerald-50 border border-emerald-100 rounded-lg flex items-start gap-2">
                        <div className="bg-emerald-200 p-1 rounded-full mt-0.5">
                          <ShieldCheck size={12} className="text-emerald-800" />
                        </div>
                        <div>
                          <span className="text-xs font-bold text-emerald-800 uppercase block mb-0.5">Primary Outcome</span>
                          <p className="text-xs font-medium text-emerald-900 leading-tight">
                            {action.expected_outcome}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <div className="p-4 border-t border-slate-100 bg-slate-50 rounded-b-2xl flex justify-end">
              <button onClick={() => setAnalysisResult(null)} className="px-6 py-2 bg-slate-200 hover:bg-slate-300 text-slate-800 font-bold rounded-lg transition-colors">
                Close Report
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 1. HEADER & SEARCH */}
      <header className="bg-emerald-900 text-white p-6 shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-500 rounded-lg">
              <MapIcon size={24} className="text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">WildSight<span className="text-emerald-400">.AI</span></h1>
              <p className="text-xs text-emerald-300 uppercase tracking-widest font-medium">Planetary Health Monitor</p>
            </div>
          </div>

          <div className="flex flex-col gap-2 w-full md:w-auto">
            <form onSubmit={handleSearch} className="relative w-full md:w-96">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search Species..."
                className="w-full pl-10 pr-4 py-3 rounded-full bg-emerald-800/50 border border-emerald-700 text-emerald-50 placeholder-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400 transition-all font-medium"
              />
              <Search className="absolute left-3.5 top-3.5 text-emerald-400" size={20} />
              <button type="submit" className="absolute right-2 top-2 bg-emerald-500 hover:bg-emerald-400 text-emerald-950 font-bold px-4 py-1.5 rounded-full text-sm transition-colors">
                LOCATE
              </button>
            </form>
            {error && <div className="text-center text-red-300 text-xs font-bold bg-red-900/30 py-1 rounded">{error}</div>}
          </div>
        </div>

        {/* Quick Links for Demo */}
        <div className="max-w-7xl mx-auto mt-4 flex gap-2 overflow-x-auto pb-2 custom-scrollbar">
          {Object.keys(MOCK_DB).map(name => (
            <button key={name} onClick={() => loadSpecies(name)} className="whitespace-nowrap px-3 py-1 bg-emerald-800/50 hover:bg-emerald-700 rounded-full text-xs text-emerald-200 transition-colors">
              {name}
            </button>
          ))}
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-4 md:p-6 space-y-8">

        {/* 2. MAP & SPECIES CARD */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[500px]">
          {/* LEFT: MAP */}
          <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden relative group">
            <div className="absolute top-4 left-4 z-[400] bg-white/90 backdrop-blur px-4 py-2 rounded-lg shadow-md border border-slate-100 pointer-events-auto">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span className="text-xs font-bold text-slate-600 uppercase">Live Tracking Active</span>
              </div>
              <p className="text-sm font-bold text-slate-800 mt-1">
                {activeSpecies.checkpoints.length} Checkpoints Identified
              </p>
              {activeSpecies.occupancy_probability !== undefined && (
                <div className="mt-2 pt-2 border-t border-slate-200">
                  <p className="text-xs font-bold text-slate-500 uppercase">AI Habitat Viability</p>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-full bg-slate-200 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500 transition-all duration-1000" style={{ width: `${activeSpecies.occupancy_probability * 100}%` }}></div>
                    </div>
                    <span className="text-emerald-700 font-bold">{(activeSpecies.occupancy_probability * 100).toFixed(0)}%</span>
                  </div>
                </div>
              )}
            </div>

            {/* ANALYZE BUTTON */}
            <button
              onClick={runZoneAnalysis}
              disabled={analyzing}
              className="absolute bottom-6 right-6 z-[400] bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-full shadow-lg font-bold flex items-center gap-2 transition-transform hover:scale-105 active:scale-95 disabled:opacity-70 disabled:cursor-wait"
            >
              {analyzing ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Lightbulb size={20} />}
              {analyzing ? 'Processing...' : 'Analyze Habitat Zone'}
            </button>

            <MapContainer center={[activeSpecies.location.lat, activeSpecies.location.lon]} zoom={activeSpecies.location.zoom} style={{ height: '100%', width: '100%' }} zoomControl={false}>
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap" />
              <MapUpdater center={[activeSpecies.location.lat, activeSpecies.location.lon]} zoom={activeSpecies.location.zoom} />
              {activeSpecies.checkpoints.map((pt, i) => (
                <Marker key={i} position={[pt.lat, pt.lon]}>
                  <Popup className="font-sans">
                    <strong>{activeSpecies.name}</strong><br />
                    Confidence: {pt.conf * 100}%
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>

          {/* RIGHT: SPECIES OVERVIEW */}
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col">
            <div className="mb-6">
              <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-2 ${activeSpecies.status === 'Endangered' || activeSpecies.status === 'Critically Endangered' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                {activeSpecies.status}
              </span>
              <h2 className="text-3xl font-serif text-slate-900 leading-tight mb-2">{activeSpecies.name}</h2>
            </div>

            {/* POPULATION CHART (User Request) */}
            <div className="h-40 mb-4 w-full">
              <Line data={{
                labels: activeSpecies.years,
                datasets: [{
                  label: 'Count',
                  data: activeSpecies.population,
                  borderColor: '#3b82f6',
                  backgroundColor: 'rgba(59, 130, 246, 0.1)',
                  fill: true,
                  tension: 0.4
                }]
              }} options={popOptions} />
            </div>

            <div className="mt-auto bg-slate-50 rounded-xl p-4 border border-slate-100">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-bold uppercase text-slate-400">Current Est.</span>
                <span className="text-lg font-bold text-slate-800">{activeSpecies.population[4]}</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-1.5">
                <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: '60%' }}></div>
              </div>
            </div>
          </div>
        </section>

        {/* 3. HABITAT ANALYTICS ENGINE */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <Activity className="text-emerald-600" />
            <h2 className="text-2xl font-bold text-slate-900">Habitat Analytics Engine</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

            {/* CARD 1: VEGETATION */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
              <div className="flex justify-between items-start mb-4">
                <div className="bg-green-100 p-2 rounded-lg"><TreeDeciduous className="text-green-600" size={20} /></div>
                <span className="text-xs font-bold text-slate-400 uppercase">Biomass</span>
              </div>
              <h3 className="text-lg font-bold text-slate-800 mb-4">Vegetation Indices</h3>
              <div className="h-48">
                <Line data={{
                  labels: activeSpecies.years,
                  datasets: [
                    { label: 'NDVI (Greenness)', data: activeSpecies.analysis.vegetation.ndvi, borderColor: '#10b981', tension: 0.4 },
                    { label: 'EVI (Health)', data: activeSpecies.analysis.vegetation.evi, borderColor: '#059669', borderDash: [5, 5], tension: 0.4 }
                  ]
                }} options={vegOptions} />
              </div>
            </div>

            {/* CARD 2: CLIMATE */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
              <div className="flex justify-between items-start mb-4">
                <div className="bg-blue-100 p-2 rounded-lg"><Thermometer className="text-blue-600" size={20} /></div>
                <span className="text-xs font-bold text-slate-400 uppercase">CMIP6 Model</span>
              </div>
              <h3 className="text-lg font-bold text-slate-800 mb-4">Climate Forecast (5yr)</h3>
              <div className="h-48">
                <Line data={{
                  labels: ['2025', '2026', '2027', '2028', '2029'],
                  datasets: [
                    { label: 'Temp (°C)', data: activeSpecies.analysis.climate.temp, borderColor: '#ef4444', yAxisID: 'y' },
                    { label: 'Rainfall (mm)', data: activeSpecies.analysis.climate.rain, borderColor: '#3b82f6', yAxisID: 'y1' }
                  ]
                }} options={{
                  ...climateOptions,
                  scales: {
                    y: { position: 'left', title: { display: true, text: 'Temp' } },
                    y1: { position: 'right', title: { display: true, text: 'Rain' }, grid: { drawOnChartArea: false } }
                  }
                }} />
              </div>
            </div>

            {/* CARD 3: DISTURBANCE */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
              <div className="flex justify-between items-start mb-4">
                <div className="bg-orange-100 p-2 rounded-lg"><Flame className="text-orange-600" size={20} /></div>
                <span className="text-xs font-bold text-slate-400 uppercase">Risk</span>
              </div>
              <h3 className="text-lg font-bold text-slate-800 mb-4">Disturbance Factors</h3>
              <div className="h-48">
                <Bar data={{
                  labels: activeSpecies.years,
                  datasets: [
                    { label: 'Fire Power (FRP)', data: activeSpecies.analysis.disturbance.frp, backgroundColor: '#f97316' },
                    { label: 'Night Lights (Urban)', data: activeSpecies.analysis.disturbance.nightlight, backgroundColor: '#6366f1' }
                  ]
                }} options={disturbOptions} />
              </div>
            </div>

          </div>
        </section>

        {/* 4. PRESERVATION ADVICE (Simple Terms) */}
        <section className="bg-indigo-900 rounded-3xl p-8 md:p-12 text-white relative overflow-hidden">
          {/* Background Decoration */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-600 rounded-full blur-[100px] opacity-30 pointer-events-none"></div>

          <div className="relative z-10 grid md:grid-cols-3 gap-10">
            <div className="md:col-span-1">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-800 rounded-full border border-indigo-700 mb-6">
                <ShieldCheck size={18} className="text-indigo-300" />
                <span className="text-xs font-bold uppercase tracking-widest text-indigo-200">Preservation Plan</span>
              </div>
              <h2 className="text-3xl font-bold font-serif leading-tight mb-4">Recommended Actions</h2>
              <p className="text-indigo-200 leading-relaxed">
                AI-generated preservation strategy based on the analyzed vegetation, climate, and disturbance data.
              </p>
            </div>

            <div className="md:col-span-2 grid gap-4">
              {activeSpecies.advice.map((tip, idx) => (
                <div key={idx} className="flex items-start gap-4 p-4 bg-indigo-800/50 rounded-xl border border-indigo-700/50 hover:bg-indigo-800 transition-colors cursor-default">
                  <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-300 font-bold shrink-0 mt-1">
                    {idx + 1}
                  </div>
                  <div className="text-indigo-100 font-medium pt-1 whitespace-pre-wrap leading-relaxed w-full">
                    {tip.split('\n').map((line, i) => {
                      // Bold headers
                      if (line.trim().startsWith('###') || line.trim().startsWith('**')) {
                        return <p key={i} className="font-bold text-white mb-1 mt-1 first:mt-0">{line.replace(/###/g, '').replace(/\*\*/g, '')}</p>;
                      }
                      // Outcome highlighting in this dark theme
                      if (line.trim().startsWith('- **Outcome**:')) {
                        return (
                          <div key={i} className="mt-2 text-xs font-bold text-emerald-300 bg-emerald-900/30 border border-emerald-500/30 px-3 py-2 rounded inline-block">
                            {line.replace('- **Outcome**:', '🎯 TARGET:')}
                          </div>
                        );
                      }
                      return <span key={i} className="block min-h-[1rem]">{line}</span>;
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

      </main>
    </div>
  );
}

export default App;
