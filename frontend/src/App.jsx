import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import UserProfile from './UserProfile';
import Login from './pages/Login';
import Register from './pages/Register';
import axios from 'axios';
import { auth as firebaseAuth } from './firebase';
import { onAuthStateChanged } from 'firebase/auth';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, useMap } from 'react-leaflet';
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
  Users,
  Leaf,
  Bird,
  Cat,
  ChevronLeft,
  ChevronRight,
  BrainCircuit,
  MapPin,
  List,
  Navigation,
  User,
  X,
  FileText,
  Download
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

// --- UTILS ---
const generateTrend = (baseValue, variance, count = 5) => {
  return Array.from({ length: count }, () => {
    const noise = (Math.random() - 0.5) * variance;
    return Number((baseValue + noise).toFixed(2));
  });
};

const QUICK_LINKS = [
  { name: "Bengal Tiger", icon: <Cat size={14} />, type: "Mammal" },
  { name: "Asian Elephant", icon: <Users size={14} />, type: "Mammal" },
  { name: "Syzygium travancoricum", icon: <Leaf size={14} />, type: "Plant" },
  { name: "Great Indian Bustard", icon: <Bird size={14} />, type: "Bird" },
];

function MapUpdater({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, zoom, { duration: 0.8 });
  }, [center, zoom, map]);
  return null;
}

function Dashboard() {
  const navigate = useNavigate();
  const [speciesName, setSpeciesName] = useState('Indian Tiger');
  const [activeSpecies, setActiveSpecies] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedZone, setSelectedZone] = useState(null); // New State for Cluster Selection
  const [user, setUser] = useState(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(firebaseAuth, async (user) => {
      if (user) {
        const token = await user.getIdToken();
        localStorage.setItem('wildsight_token', token);
        try {
          const res = await axios.get('http://localhost:8000/api/v1/auth/me', {
            headers: { Authorization: `Bearer ${token}` }
          });
          setUser(res.data);
        } catch (e) {
          console.error("Auth sync error:", e);
        }
      } else {
        setUser(null);
        localStorage.removeItem('wildsight_token');
      }
    });
    return () => unsubscribe();
  }, []);


  const handleSearch = (e) => {
    e.preventDefault();
    if (speciesName) {
      loadSpecies(speciesName.trim());
    }
  };

  // --- API FETCH ---
  // --- MAIN DATA FETCHING ---
  const loadSpecies = async (paramName, zoneId = null, silent = false) => {
    if (!silent) {
      setLoading(true);
      setActiveSpecies(null);
    }
    setError(null);
    if (!zoneId) setSelectedZone(null); // Reset selection only for national search
    try {
      console.log(`Fetching data for: ${paramName}, Zone: ${zoneId || 'National'} (Silent: ${silent})`);

      let url = `http://localhost:8000/api/v1/species/${paramName}`;
      if (zoneId) {
        url += `?zone_id=${zoneId}`;
      }

      const response = await axios.get(url);
      const data = response.data;

      if (!data || !data.species) {
        throw new Error("No species data found in API response.");
      }

      const speciesData = data.species; // flatten structure
      const envData = data.environment_context || {};
      const rootData = data; // Keep full response for occupancy etc.

      // Map Checkpoints
      let checkpoints = speciesData.checkpoints || [];
      if (checkpoints.length === 0) {
        checkpoints = [{ lat: 20, lon: 78, id: 'mock' }];
      }

      // Auto-Center Map
      let center = [20, 78];
      let zoom = 4;

      // If Zone Selected, center on Zone.
      if (zoneId) {
        // Keep current map center or dont override
      } else if (speciesData.checkpoints_region) {
        center = [
          (speciesData.checkpoints_region.lat_min + speciesData.checkpoints_region.lat_max) / 2,
          (speciesData.checkpoints_region.lon_min + speciesData.checkpoints_region.lon_max) / 2
        ];
        zoom = 5;
      }

      // --- DYNAMIC GRAPH DATA GENERATION ---
      const baseTemp = envData.avg_temp || 25;
      const baseRain = envData.avg_rain || 1000;
      const baseNDVI = envData.avg_ndvi || 0.5;
      const baseHDI = envData.hdi || 0.3;

      const uiData = {
        id: paramName,
        name: speciesData.species_name,
        estimated_population: speciesData.estimated_population, // [Fix] Map explicitly
        status: speciesData.status || "Unknown",
        population: Array.isArray(speciesData.population_history) ? speciesData.population_history : [],
        years: speciesData.years || ['2020', '2021', '2022', '2023', '2024'],
        years_hist: speciesData.years_history || ['2020', '2021', '2022', '2023', '2024'],
        years_forecast: speciesData.years_forecast || ['2025', '2026', '2027', '2028', '2029'],

        // [New] Specific Labels
        days_vegetation: speciesData.days_vegetation || ['D1', 'D2', 'D3', 'D4', 'D5'],
        years_disturbance: speciesData.years_disturbance || ['Y1', 'Y2', 'Y3', 'Y4', 'Y5'],

        location: { lat: center[0], lon: center[1], zoom: zoom },
        occupancy_probability: rootData.occupancy_probability ?? 0,

        analysis: {
          vegetation: {
            ndvi: speciesData.analysis?.vegetation?.ndvi || [],
            evi: speciesData.analysis?.vegetation?.evi || [],
            ndwi: speciesData.analysis?.vegetation?.ndwi || []
          },
          climate: {
            temp: speciesData.analysis?.climate?.temp || [],
            rain: speciesData.analysis?.climate?.rain || []
          },
          disturbance: {
            frp: speciesData.analysis?.disturbance?.frp || [],
            nightlight: speciesData.analysis?.disturbance?.nightlight || []
          }
        },

        advice: [],
        checkpoints: checkpoints,
        distribution: speciesData.distribution_analysis || { zones: [], total_estimated_individuals: 0 },
        sensitivities: speciesData.sensitivities || {},
        pulse_history: speciesData.pulse_history || []
      };

      // Calculate Latest Count for UI Display
      let latestCount = 0;
      if (uiData.pulse_history && uiData.pulse_history.length > 0) {
        latestCount = uiData.pulse_history[0].count;
      } else if (uiData.population && uiData.population.length > 0) {
        latestCount = uiData.population[uiData.population.length - 1].count;
      }
      uiData.latestCount = latestCount;

      // FIX: Explicitly calculate pulse delta for UI
      let pDelta = 0;
      let pDir = 'stable';
      if (uiData.pulse_history && uiData.pulse_history.length >= 2) {
        pDelta = uiData.pulse_history[0].count - uiData.pulse_history[1].count;
      } else if (uiData.population && uiData.population.length >= 2) {
        pDelta = uiData.population[uiData.population.length - 1].count - uiData.population[uiData.population.length - 2].count;
      }

      if (pDelta > 0) pDir = 'up';
      if (pDelta < 0) pDir = 'down';

      uiData.pulse_delta = pDelta;
      uiData.pulse_direction = pDir;

      setActiveSpecies(uiData);
      setSpeciesName(speciesData.species_name);

    } catch (err) {
      console.error(err);
      setError(err.message);
      setActiveSpecies(null);
    } finally {
      setLoading(false);
    }
  };

  // --- CHART OPTIONS ---
  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { display: false }, ticks: { font: { size: 10 } } },
      y: { grid: { color: '#f3f4f6' }, ticks: { font: { size: 10 } } }
    }
  };

  const [analysisResult, setAnalysisResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [aiReport, setAiReport] = useState('');
  const [downloading, setDownloading] = useState(false);

  const runZoneAnalysis = async (zoneArg = null) => {
    // If called from onClick directly, zoneArg might be an event object.
    const isEvent = zoneArg && zoneArg.nativeEvent;
    const zone = (!isEvent && zoneArg?.id) ? zoneArg : (selectedZone || (activeSpecies?.distribution?.zones?.length > 0 ? activeSpecies.distribution.zones[0] : null));

    if (!zone) {
      console.warn("No zone selected for analysis. Performing global summary.");
    }

    const speciesToLoad = activeSpecies?.name || speciesName || 'Tiger';

    if (zone) {
      console.log(`Analyzing Zone: ${zone.name} (${zone.id})`);
      setSelectedZone(zone);
      // 1. SILENT RELOAD to FORCE chart update for this zone
      // Setting silent=true updates data without full loading spinner
      await loadSpecies(speciesToLoad, zone.id, true);
    }

    // 2. ML ANALYSIS & LLM REPORT (Parallel)
    setAnalyzing(true);
    setAnalysisResult(null); // Clear previous ML results immediately
    setAiReport(''); // Clear previous LLM report
    try {
      const h3Index = zone ? zone.id : "global_summary";
      const name = speciesToLoad;
      const countForAnalysis = zone ? (zone.sighting_count * 5) : (activeSpecies?.latestCount || 1000);

      console.log(`Running ML Analysis for ${name} at Zone ${h3Index}`);

      // 1. Fetch Prescriptions (Fast)
      const prescRes = await axios.get(`http://localhost:8000/api/v1/analytics/prescriptions/${h3Index}?species=${name}&count=${countForAnalysis}`);
      setAnalysisResult(prescRes.data);
      setShowModal(true); // Open modal immediately with ML results
      setAnalyzing(false); // Stop loading state for the main button

      // 2. Fetch LLM Report in Background (Pass Zone ID)
      try {
        let reportUrl = `http://localhost:8000/api/v1/analytics/report/${name}`;
        if (zone) {
          reportUrl += `?zone_id=${zone.id}`;
        }
        const reportRes = await axios.get(reportUrl);
        setAiReport(reportRes.data.report);
      } catch (e) {
        console.error("LLM Report Background Error:", e);
        setAiReport("## Analysis Service Delayed\nThe AI engine is currently under high load. Please try refreshing or check back in a moment.");
      }
    } catch (e) {
      console.error("Analysis Engine Error:", e);
      setError("Failed to generate comprehensive analysis. Please check API connectivity.");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!aiReport) return;
    setDownloading(true);
    try {
      const response = await axios.post(
        `http://localhost:8000/api/v1/analytics/report/download/${activeSpecies.name}`,
        { report_text: aiReport },
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `WildSight_Report_${activeSpecies.name}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (e) {
      console.error("Download Error:", e);
      alert("Failed to download PDF report.");
    } finally {
      setDownloading(false);
    }
  };

  useEffect(() => {
    loadSpecies('Tiger');
  }, []);

  // --- CAROUSEL LOGIC ---
  const [slideIndex, setSlideIndex] = useState(0);
  const nextSlide = () => setSlideIndex((prev) => (prev + 1) % 4);
  const prevSlide = () => setSlideIndex((prev) => (prev - 1 + 4) % 4);

  // --- RENDER ---
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1549313861-33587f3d2956?q=80&w=2670&auto=format&fit=crop')] bg-cover bg-center opacity-10 blur-sm"></div>
        <div className="text-center z-10 p-8 glass-panel rounded-2xl">
          <div className="w-16 h-16 border-4 border-emerald-500/30 border-t-emerald-400 rounded-full animate-spin mx-auto mb-6"></div>
          <h2 className="text-2xl font-bold text-white tracking-wide">Scanning Biosphere...</h2>
          <p className="text-emerald-200/70 mt-2">Connecting to Global Biodiversity Information Facility (GBIF)</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
        <div className="bg-slate-800 p-8 rounded-2xl shadow-2xl max-w-lg text-center border border-slate-700 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-500 via-orange-500 to-red-500"></div>
          <div className="w-20 h-20 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <Search size={40} className="text-red-400" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Species Not Found</h2>
          <p className="text-slate-400 mb-8 text-lg px-4">{error}</p>
          <div className="flex gap-4 justify-center">
            <button onClick={() => window.location.reload()} className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors">
              Reset
            </button>
            <button onClick={() => { setError(null); setSpeciesName('Tiger'); loadSpecies('Tiger'); }} className="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold transition-colors">
              Return to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!activeSpecies) return null;

  const slides = [
    {
      title: "Monitoring Log (5-Day Pulse)",
      icon: <Activity size={24} className="text-purple-600" />,
      bg: "bg-purple-50",
      subtitle: selectedZone ? `LOCATION SENSOR FEED: ${selectedZone.name}` : "NATIONAL TELEMETRY CLUSTER",
      chart: (
        <Line data={{
          labels: activeSpecies.pulse_history ? activeSpecies.pulse_history.map(p => p.date).reverse() : [],
          datasets: [
            {
              label: 'Estimated Count',
              data: activeSpecies.pulse_history ? activeSpecies.pulse_history.map(p => p.count).reverse() : [],
              borderColor: '#9333ea',
              backgroundColor: '#9333ea',
              borderWidth: 3,
              tension: 0.4,
              pointRadius: 4,
              yAxisID: 'y'
            },
            {
              label: 'Risk Score (ML)',
              data: activeSpecies.pulse_history ? activeSpecies.pulse_history.map(p => p.risk).reverse() : [],
              borderColor: '#f43f5e',
              backgroundColor: '#f43f5e',
              borderWidth: 2,
              borderDash: [5, 5],
              tension: 0.1,
              pointRadius: 3,
              yAxisID: 'y1'
            }
          ]
        }} options={{
          ...commonOptions,
          scales: {
            ...commonOptions.scales,
            y: { ...commonOptions.scales.y, position: 'left', title: { display: true, text: 'Pop. Count', font: { weight: 'bold' } } },
            y1: { display: true, position: 'right', grid: { display: false }, title: { display: true, text: 'Risk Index', font: { weight: 'bold' } }, min: 0, max: 1 }
          }
        }} />
      )
    },
    {
      title: "Vegetation & Moisture",
      icon: <TreeDeciduous size={24} className="text-emerald-600" />,
      bg: "bg-emerald-50",
      subtitle: selectedZone ? `LOCAL SPECTRAL FEED: ${selectedZone.name}` : "NATIONAL SPECTRAL BANDS (5 Days)",
      chart: (
        <Line data={{
          labels: activeSpecies.days_vegetation,
          datasets: [
            {
              label: 'NDVI (Greenness)',
              data: activeSpecies.analysis.vegetation.ndvi,
              borderColor: '#10b981',
              backgroundColor: '#10b981',
              tension: 0.4,
              fill: false
            },
            {
              label: 'NDWI (Water)',
              data: activeSpecies.analysis.vegetation.ndwi,
              borderColor: '#0284c7',
              backgroundColor: '#0284c7',
              borderDash: [5, 5],
              tension: 0.4,
              fill: false
            }
          ]
        }} options={commonOptions} />
      )
    },
    {
      title: "Climate Resilience",
      icon: <Thermometer size={24} className="text-blue-600" />,
      bg: "bg-blue-50",
      subtitle: selectedZone ? `LOCAL METEOROLOGY: ${selectedZone.name}` : "NATIONAL CLIMATE FORECAST (5 Years)",
      chart: (
        <Line data={{
          labels: activeSpecies.years_forecast,
          datasets: [
            {
              label: 'Temp (°C)',
              data: activeSpecies.analysis.climate.temp,
              borderColor: '#ef4444',
              backgroundColor: '#ef4444',
              yAxisID: 'y',
              tension: 0.4
            },
            {
              label: 'Rain (mm)',
              data: activeSpecies.analysis.climate.rain,
              borderColor: '#3b82f6',
              backgroundColor: '#3b82f6',
              yAxisID: 'y1',
              tension: 0.4
            }
          ]
        }} options={{
          ...commonOptions,
          scales: {
            ...commonOptions.scales,
            y: { ...commonOptions.scales.y, position: 'left', title: { display: true, text: 'Temp' } },
            y1: { display: true, position: 'right', grid: { display: false }, title: { display: true, text: 'Rain' } }
          }
        }} />
      )
    },
    {
      title: "Disturbance Factors",
      icon: <Flame size={24} className="text-orange-600" />,
      bg: "bg-orange-50",
      subtitle: selectedZone ? `LOCAL DISTURBANCE: ${selectedZone.name}` : "NATIONAL ANTHROPOGENIC IMPACT (5 Years)",
      chart: (
        <Bar data={{
          labels: activeSpecies.years_disturbance,
          datasets: [
            {
              label: 'Fire Power (FRP)',
              data: activeSpecies.analysis.disturbance.frp,
              backgroundColor: '#f97316',
              borderRadius: 4,
              barPercentage: 0.5
            },
            {
              label: 'Night Lights',
              data: activeSpecies.analysis.disturbance.nightlight,
              backgroundColor: '#6366f1',
              borderRadius: 4,
              barPercentage: 0.5
            }
          ]
        }} options={commonOptions} />
      )
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-800 pb-10 relative">

      {/* MODAL FOR ML RESULTS */}
      {showModal && analysisResult && (
        <div className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[85vh] overflow-y-auto animate-in fade-in zoom-in duration-300">
            <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-900 text-white sticky top-0 z-10">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-emerald-500/20 rounded-lg">
                  <BrainCircuit className="text-emerald-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold">EcoGuard ML Prescription</h3>
                  <p className="text-xs text-slate-400 uppercase tracking-wider">Generated by Random Forest Classifier</p>
                </div>
              </div>
              <button onClick={() => setShowModal(false)} className="p-2 hover:bg-white/10 rounded-full transition-colors"><X /></button>
            </div>

            <div className="p-8 space-y-8">
              {/* AI REPORT SECTION (LLM) */}
              <div className="p-6 bg-slate-900 text-white rounded-2xl border border-slate-700 relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                  <BrainCircuit size={80} />
                </div>
                <div className="flex justify-between items-center mb-6">
                  <h4 className="text-xl font-bold flex items-center gap-2">
                    <FileText className="text-emerald-400" />
                    AI Conservation Analysis
                  </h4>
                  <button
                    onClick={handleDownloadPDF}
                    disabled={downloading || !aiReport}
                    className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 text-white rounded-xl text-sm font-bold transition-all shadow-lg shadow-emerald-500/20"
                  >
                    {downloading ? (
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                      <Download size={16} />
                    )}
                    Export PDF
                  </button>
                </div>

                <div className="prose prose-invert prose-emerald max-w-none text-slate-300">
                  {aiReport ? (
                    aiReport.split('\n').map((line, idx) => {
                      const cleanLine = line.trim();
                      if (!cleanLine) return <br key={idx} />;

                      // Headings
                      if (cleanLine.startsWith('# ')) return <h2 key={idx} className="text-2xl font-bold text-white mt-6 mb-4">{cleanLine.slice(2)}</h2>;
                      if (cleanLine.startsWith('## ')) return <h3 key={idx} className="text-xl font-bold text-emerald-400 mt-5 mb-3">{cleanLine.slice(3)}</h3>;
                      if (cleanLine.startsWith('### ')) return <h4 key={idx} className="text-lg font-bold text-white mt-4 mb-2">{cleanLine.slice(4)}</h4>;

                      // List Items
                      if (cleanLine.startsWith('* ') || cleanLine.startsWith('- ')) {
                        return (
                          <li key={idx} className="ml-4 mb-1 list-disc text-slate-300">
                            {cleanLine.slice(2).split(/(\*\*.*?\*\*)/g).map((part, pi) =>
                              part.startsWith('**') ? <strong key={pi} className="text-white">{part.slice(2, -2)}</strong> : part
                            )}
                          </li>
                        );
                      }

                      // Paragraph with bolding
                      return (
                        <p key={idx} className="mb-3 leading-relaxed">
                          {cleanLine.split(/(\*\*.*?\*\*)/g).map((part, pi) =>
                            part.startsWith('**') ? <strong key={pi} className="text-white">{part.slice(2, -2)}</strong> : part
                          )}
                        </p>
                      );
                    })
                  ) : (
                    <div className="flex flex-col items-center py-10 text-slate-500">
                      <div className="w-8 h-8 border-2 border-slate-700 border-t-emerald-500 rounded-full animate-spin mb-4" />
                      <p className="animate-pulse">Synthesizing intelligence from satellite and census data...</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Risk Assessment & Prescriptions (ML) */}
              <div className="grid md:grid-cols-2 gap-6">
                <div className="flex items-center gap-6 p-6 bg-slate-50 rounded-xl border border-slate-200">
                  <div className="text-center">
                    <div className="text-4xl font-black text-slate-900">{(analysisResult.risk_assessment.risk_score * 100).toFixed(0)}<span className="text-lg text-slate-400">%</span></div>
                    <div className="text-xs font-bold uppercase text-slate-500">Risk Index</div>
                  </div>
                  <div className="h-12 w-[1px] bg-slate-200"></div>
                  <div>
                    <h4 className="font-bold text-slate-800 mb-1">Stressor: <span className="text-red-500 uppercase">{analysisResult.risk_assessment.primary_stressor}</span></h4>
                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Anomaly: {analysisResult.risk_assessment.anomaly_detected ? 'DETECTED ⚠️' : 'NONE'}</p>
                  </div>
                </div>

                <div className="flex flex-col justify-center p-6 bg-emerald-50 rounded-xl border border-emerald-100">
                  <h4 className="text-xs font-black text-emerald-800 uppercase tracking-widest mb-2">Model Confidence</h4>
                  <div className="w-full bg-emerald-200 h-2 rounded-full overflow-hidden">
                    <div className="bg-emerald-600 h-full" style={{ width: '95%' }}></div>
                  </div>
                  <p className="text-[10px] text-emerald-700 mt-2 font-bold">Inference based on Random Forest v2.0</p>
                </div>
              </div>

              {/* Actions */}
              <div className="space-y-4">
                <h4 className="font-bold text-slate-700 flex items-center gap-2">
                  <ShieldCheck className="text-emerald-600" /> ML-Optimized Intervention Plan
                </h4>
                {analysisResult.recommended_actions.map((action, i) => (
                  <div key={i} className="border border-slate-100 bg-white rounded-xl p-6 shadow-sm">
                    <div className="flex justify-between items-start mb-4">
                      <span className="px-3 py-1 bg-slate-100 text-slate-800 rounded-full text-[10px] font-black uppercase tracking-widest">{action.action_type.replace(/_/g, ' ')}</span>
                      <span className="font-mono text-emerald-600 text-xs font-bold">${action.estimated_cost.toLocaleString()}</span>
                    </div>
                    <div className="text-sm text-slate-600 leading-relaxed">
                      {action.description.replace(/###/g, '').split('\n').filter(l => l.trim()).map((line, idx) => (
                        <p key={idx} className="mb-2 last:mb-0">
                          {line.split(/(\*\*.*?\*\*)/g).map((part, pi) =>
                            part.startsWith('**') ? <strong key={pi} className="text-slate-900">{part.slice(2, -2)}</strong> : part
                          )}
                        </p>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-6 bg-slate-50 border-t border-slate-100 flex justify-end gap-4">
              <button
                onClick={handleDownloadPDF}
                disabled={downloading || !aiReport}
                className="px-6 py-2 bg-white border border-slate-200 text-slate-700 font-bold rounded-xl hover:bg-slate-50 transition-colors flex items-center gap-2"
              >
                <Download size={18} />
                Download Report
              </button>
              <button className="flex-1 py-3 px-4 bg-slate-900 text-white rounded-2xl font-black text-sm uppercase tracking-widest hover:bg-slate-800 transition-all shadow-xl shadow-slate-900/10 flex items-center justify-center gap-2">
                <Navigation size={16} className="text-emerald-400" />
                National Baseline
              </button>
              <button onClick={() => setShowModal(false)} className="px-8 py-2 bg-slate-900 text-white font-bold rounded-xl hover:bg-slate-800 transition-all">
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* HEADER */}
      <header className="bg-slate-900 text-white shadow-2xl sticky top-0 z-50 overflow-hidden border-b border-slate-800">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-4 group cursor-pointer" onClick={() => loadSpecies('Tiger')}>
              <div className="p-3 bg-gradient-to-tr from-emerald-500 to-teal-400 rounded-2xl shadow-lg shadow-emerald-500/20 group-hover:rotate-3 transition-transform">
                <MapIcon size={32} className="text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-black text-white tracking-tight leading-none">WILD<span className="text-emerald-400">SIGHT</span> <span className="text-xs align-top bg-emerald-100/10 text-emerald-400 px-2 py-1 rounded-md ml-1 tracking-widest font-black uppercase">India</span></h1>
                <p className="text-[10px] text-emerald-200/60 uppercase tracking-[0.3em] font-black">National Intelligence</p>
              </div>
            </div>

            <div className="flex-1 max-w-2xl w-full">
              <form onSubmit={handleSearch} className="relative group">
                <input
                  type="text"
                  value={speciesName}
                  onChange={(e) => setSpeciesName(e.target.value)}
                  placeholder="Search Indian Species (e.g. Bengal Tiger, Great Indian Bustard)..."
                  className="w-full bg-slate-800/80 border-2 border-slate-700/50 rounded-2xl py-4 pl-14 pr-32 text-lg focus:outline-none focus:border-emerald-500/50 focus:bg-slate-800 transition-all placeholder:text-slate-500"
                />
                <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-emerald-400 transition-colors" size={24} />
                <button type="submit" className="absolute right-3 top-1/2 -translate-y-1/2 px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-black rounded-xl text-sm transition-all">
                  SCAN
                </button>
              </form>
            </div>

            <div className="hidden lg:flex items-center gap-6">
              {user ? (
                <button
                  onClick={() => navigate('/profile')}
                  className="flex items-center gap-3 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-2xl border border-slate-700 transition-all text-slate-200 group"
                >
                  <div className="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center font-bold text-white uppercase shadow-lg shadow-emerald-500/20 group-hover:scale-110 transition-transform">
                    {user.full_name.charAt(0)}
                  </div>
                  <span className="text-sm font-bold">{user.full_name.split(' ')[0]}</span>
                </button>
              ) : (
                <button
                  onClick={() => navigate('/login')}
                  className="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-black rounded-xl text-sm transition-all shadow-lg shadow-emerald-600/20"
                >
                  SIGN IN
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* SPECIES NAVIGATION BAR - SCALED UP */}
      <nav className="bg-slate-800 text-white border-b border-slate-700 overflow-hidden shadow-inner">
        <div className="max-w-[1600px] mx-auto flex items-center gap-2 overflow-x-auto no-scrollbar py-4 px-6">
          <div className="flex-none pr-4 border-r border-slate-700 mr-2">
            <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">Fast Reach</span>
          </div>
          {QUICK_LINKS.map(link => (
            <button
              key={link.name}
              onClick={() => loadSpecies(link.name)}
              className={`flex-none flex items-center gap-3 px-6 py-3 rounded-2xl border-2 transition-all font-bold group ${activeSpecies?.name === link.name
                ? 'bg-emerald-500 border-emerald-400 text-white shadow-lg shadow-emerald-500/20 scale-105'
                : 'bg-slate-900/50 border-slate-700 text-slate-400 hover:border-slate-500 hover:text-white'
                }`}
            >
              <div className={`p-1.5 rounded-lg ${activeSpecies?.name === link.name ? 'bg-white/20' : 'bg-slate-800 text-emerald-500'}`}>
                {link.icon}
              </div>
              <span className="text-base">{link.name}</span>
            </button>
          ))}

          <div className="flex-none px-4 opacity-20 text-slate-500">|</div>

          {['Lion', 'Leopard', 'Snow Leopard', 'Rhino', 'Gharial'].map(s => (
            <button
              key={s}
              onClick={() => loadSpecies(s)}
              className="flex-none px-6 py-3 bg-slate-900/30 border border-slate-700/50 rounded-2xl text-sm font-bold text-slate-500 hover:text-white hover:border-emerald-500/50 transition-all whitespace-nowrap"
            >
              {s}
            </button>
          ))}
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-4 md:p-6 space-y-8">

        {/* TOP ROW: MAP & STATUS */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[500px]">
          {/* LEFT: MAP */}
          <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden relative group">
            {/* Map Overlay Info */}
            <div className="absolute top-4 left-4 z-[400]">
              <div className="bg-white/90 backdrop-blur-md p-3 rounded-xl shadow-lg border border-slate-100/50">
                <div className="flex items-center gap-2 mb-1">
                  <span className="relative flex h-2.5 w-2.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                  </span>
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wide">Live Feed</span>
                </div>
                <div className="text-sm font-bold text-slate-800">
                  {activeSpecies.checkpoints.length} Checkpoints Found
                </div>
              </div>
            </div>

            <MapContainer center={[activeSpecies.location.lat, activeSpecies.location.lon]} zoom={activeSpecies.location.zoom} style={{ height: '100%', width: '100%' }} zoomControl={false}>
              <TileLayer
                url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
              />
              <MapUpdater center={[activeSpecies.location.lat, activeSpecies.location.lon]} zoom={activeSpecies.location.zoom} />

              {/* RENDER CLUSTERS */}
              {activeSpecies.distribution?.zones.map((zone, i) => (
                <CircleMarker
                  key={i}
                  center={[zone.lat, zone.lon]}
                  radius={Math.min(zone.sighting_count * 3, 30)}
                  pathOptions={{
                    color: activeSpecies.checkpoints_region ? "#10b981" : "#f59e0b",
                    fillColor: activeSpecies.checkpoints_region ? "#10b981" : "#f59e0b",
                    fillOpacity: 0.6
                  }}
                  eventHandlers={{
                    click: () => {
                      console.log(`Zone Clicked: ${zone.name} (${zone.id})`);
                      setSelectedZone(zone);
                      // Trigger SILENT reload for the specific zone to get local analytics/graphs
                      loadSpecies(activeSpecies.name, zone.id, true);
                    }
                  }}
                >
                  <Popup>
                    <div className="text-center p-1">
                      <strong className="text-slate-800">{zone.name}</strong><br />
                      <span className="text-xs text-slate-500">{zone.sighting_count} Sightings</span><br />
                      <button onClick={() => runZoneAnalysis(zone)} className="mt-2 px-2 py-1 bg-emerald-600 text-white rounded text-xs font-bold">Analyze Habitat</button>
                    </div>
                  </Popup>
                </CircleMarker>
              ))}

              {/* RENDER INDIVIDUAL POINTS (Ghosted if Clusters exist) */}
              {activeSpecies.checkpoints.map((pt, i) => (
                <Marker key={i} position={[pt.lat, pt.lon]} opacity={activeSpecies.distribution?.zones.length > 0 ? 0.4 : 1.0}>
                  <Popup>
                    <div className="text-center p-1">
                      <strong className="text-emerald-700">{activeSpecies.name}</strong><br />
                      <span className="text-xs text-slate-500">{pt.lat.toFixed(2)}, {pt.lon.toFixed(2)}</span>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>

          {/* RIGHT: SPECIES CARD */}
          <div className="bg-white p-0 rounded-2xl shadow-sm border border-slate-200 flex flex-col overflow-hidden">
            <div className="p-6 pb-0">
              <div className="flex justify-between items-start mb-4">
                <span className={`inline-flex px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${activeSpecies.status.includes('Endangered') || activeSpecies.status.includes('Threatened')
                  ? 'bg-red-50 text-red-600 border border-red-100'
                  : 'bg-green-50 text-green-600 border border-green-100'
                  }`}>
                  {activeSpecies.status}
                </span>
                <button className="text-slate-400 hover:text-emerald-500 transition-colors"><Activity size={18} /></button>
              </div>
              <h2 className="text-4xl font-serif text-slate-900 leading-none mb-1">{activeSpecies.name}</h2>

              <div className="flex items-baseline gap-2 mt-2 mb-1">
                <span className="text-4xl font-black text-emerald-600 tracking-tighter">
                  {activeSpecies.estimated_population > 0
                    ? activeSpecies.estimated_population.toLocaleString()
                    : (activeSpecies.distribution?.total_estimated_individuals?.toLocaleString() || "Unknown")}
                </span>
                <span className="text-xs text-slate-500 font-black uppercase tracking-widest">Today's Est. Count</span>
                {activeSpecies.pulse_history && activeSpecies.pulse_history.length > 0 && (
                  <span className="text-[10px] px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded-full font-bold">
                    Live Update: {activeSpecies.pulse_history[0].date}
                  </span>
                )}
              </div>
              <div className="mb-4">
                <span className="text-[10px] uppercase font-bold text-slate-400 border border-slate-200 px-2 py-1 rounded-lg bg-slate-50">
                  Source: {activeSpecies.estimated_population > 0 ? "Verified Census Baseline (Adj. Real-Time)" : "AI-Driven Estimate (GBIF)"}
                </span>
              </div>

              <div className="flex items-center gap-2">
                <span className={`text-xs font-black flex items-center gap-1 ${activeSpecies.pulse_direction === 'up' ? 'text-emerald-600' : (activeSpecies.pulse_direction === 'down' ? 'text-red-500' : 'text-slate-400')}`}>
                  {activeSpecies.pulse_direction === 'up' && <ChevronRight className="-rotate-90" size={12} />}
                  {activeSpecies.pulse_direction === 'down' && <ChevronRight className="rotate-90" size={12} />}
                  <span className="font-mono">
                    {activeSpecies.pulse_delta !== 0
                      ? `${activeSpecies.pulse_delta > 0 ? '+' : ''}${activeSpecies.pulse_delta} in last 5 days`
                      : 'Stable (No change)'}
                  </span>
                </span>
                <div className="h-1 w-1 rounded-full bg-slate-200"></div>
                <p className="text-xs text-slate-400 font-bold uppercase tracking-widest leading-none">National Pulse</p>
              </div>
            </div>

            <div className="flex-1 w-full h-full min-h-[180px] px-2">
              <Line data={{
                labels: activeSpecies.pulse_history && activeSpecies.pulse_history.length > 0 ? activeSpecies.pulse_history.map(p => p.date).reverse() : activeSpecies.years,
                datasets: [{
                  label: 'Estimated Count',
                  data: activeSpecies.pulse_history && activeSpecies.pulse_history.length > 0 ? activeSpecies.pulse_history.map(p => p.count).reverse() : (activeSpecies.population.length > 0 ? activeSpecies.population.map(p => p.count) : [0, 0, 0, 0, 0]),
                  borderColor: '#10b981',
                  backgroundColor: (context) => {
                    const ctx = context.chart.ctx;
                    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
                    gradient.addColorStop(0, 'rgba(16, 185, 129, 0.2)');
                    gradient.addColorStop(1, 'rgba(16, 185, 129, 0)');
                    return gradient;
                  },
                  fill: true,
                  tension: 0.4,
                  pointRadius: 4,
                  pointBackgroundColor: '#fff',
                  pointBorderColor: '#10b981',
                  pointBorderWidth: 2
                }]
              }} options={commonOptions} />
            </div>

            <div className="bg-slate-50 p-4 border-t border-slate-100 flex-1 overflow-y-auto max-h-[200px]">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1"><MapPin size={12} /> Top Habitats</h4>
              <ul className="space-y-2">
                {activeSpecies.distribution?.zones.slice(0, 5).map(zone => (
                  <li key={zone.id}
                    onClick={() => {
                      setSelectedZone(zone);
                      loadSpecies(activeSpecies.name, zone.id, true);
                    }}
                    className={`flex justify-between items-center p-2 rounded-lg cursor-pointer transition-colors ${selectedZone?.id === zone.id ? 'bg-emerald-100 border border-emerald-200' : 'bg-white border border-slate-100 hover:bg-slate-50'}`}>
                    <div>
                      <div className="text-xs font-bold text-slate-700">{zone.name}</div>
                      <div className="text-[10px] text-slate-400">{zone.lat}, {zone.lon}</div>
                    </div>
                    <span className="text-xs font-mono font-bold text-emerald-600">{zone.sighting_count}</span>
                  </li>
                ))}
                {activeSpecies.distribution?.zones.length === 0 && <li className="text-xs text-slate-400 italic">No clusters found.</li>}
              </ul>
            </div>
          </div>
        </section>

        {/* MIDDLE ROW: CAROUSEL ANALYTICS */}
        <section>
          <div className="flex justify-between items-end mb-4">
            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
              <Activity size={20} className="text-emerald-500" />
              Habitat Analytics Engine
            </h3>
            <div className="flex gap-2">
              <button onClick={prevSlide} className="p-2 bg-white border border-slate-200 rounded-full hover:bg-slate-50 text-slate-600 transition-colors shadow-sm"><ChevronLeft size={16} /></button>
              <button onClick={nextSlide} className="p-2 bg-white border border-slate-200 rounded-full hover:bg-slate-50 text-slate-600 transition-colors shadow-sm"><ChevronRight size={16} /></button>
            </div>
          </div>

          {/* CAROUSEL CONTAINER */}
          <div className="relative overflow-hidden h-[300px] bg-white rounded-3xl border border-slate-200 shadow-sm">
            <div className="absolute inset-0 flex transition-transform duration-500 ease-in-out" style={{ transform: `translateX(-${slideIndex * 100}%)` }}>
              {slides.map((slide, i) => (
                <div key={i} className="min-w-full h-full p-8 flex flex-col justify-between">
                  <div className="flex justify-between items-start">
                    <div className="flex items-center gap-4">
                      <div className={`p-3 rounded-2xl ${slide.bg} text-slate-700`}>{slide.icon}</div>
                      <div>
                        <h4 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
                          {slide.title}
                          {selectedZone && (
                            <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full border border-emerald-200 uppercase tracking-tighter">
                              Zone: {selectedZone.name}
                            </span>
                          )}
                        </h4>
                        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">{slide.subtitle}</p>
                      </div>
                    </div>
                  </div>
                  <div className="flex-1 w-full mt-6">
                    {slide.chart}
                  </div>
                </div>
              ))}
            </div>

            {/* DOTS */}
            <div className="absolute bottom-4 left-0 right-0 flex justify-center gap-2">
              {slides.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setSlideIndex(i)}
                  className={`w-2 h-2 rounded-full transition-all ${i === slideIndex ? 'bg-emerald-500 w-6' : 'bg-slate-300'}`}
                />
              ))}
            </div>
          </div>
        </section>

        {/* BOTTOM ROW: EXPLAINABLE AI */}
        <section className="bg-slate-900 rounded-3xl p-8 md:p-10 text-white relative overflow-hidden shadow-2xl">
          <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-emerald-600/20 rounded-full blur-[120px] pointer-events-none"></div>

          <div className="relative z-10 grid lg:grid-cols-12 gap-10 items-center">
            <div className="lg:col-span-8">
              <div className="inline-flex items-center gap-3 px-4 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full mb-6">
                <BrainCircuit size={16} className="text-emerald-400" />
                <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-100">Explainable AI Core</span>
              </div>
              <h2 className="text-4xl font-serif leading-tight mb-4 text-white">Generate ML-Driven Strategy</h2>
              <p className="text-slate-400 leading-relaxed text-lg max-w-2xl">
                Activate the EcoGuard Neural Engine to process satellite telemetry and historical intervention data. Our Random Forest model will predict the optimal conservation strategy for <span className="text-emerald-400 font-bold">{activeSpecies.name}</span>.
              </p>
            </div>

            <div className="lg:col-span-4 flex justify-end">
              <button
                onClick={runZoneAnalysis}
                disabled={analyzing}
                className="group relative bg-white text-slate-900 px-8 py-4 rounded-2xl font-bold text-lg w-full md:w-auto hover:bg-emerald-50 transition-all shadow-[0_0_40px_-10px_rgba(16,185,129,0.5)] flex items-center justify-center gap-3 overflow-hidden"
              >
                {analyzing ? (
                  <>
                    <div className="w-5 h-5 border-2 border-slate-900/30 border-t-slate-900 rounded-full animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    Run Analysis <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </div>
          </div>
        </section>

      </main>
    </div >
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/profile" element={<UserProfile />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </BrowserRouter>
  );
}
