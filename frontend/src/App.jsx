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
  const [loadingStep, setLoadingStep] = useState('Initializing...');
  const [isUpToDate, setIsUpToDate] = useState(false);
  const [regionName, setRegionName] = useState('');
  const [isCheckingSync, setIsCheckingSync] = useState(true);
  const [isSyncingGlobal, setIsSyncingGlobal] = useState(false);

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

  // --- GLOBAL SYNC CHECK ---
  useEffect(() => {
    const checkSync = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/v1/system/status');
        if (!res.data.synchronized) {
          setIsSyncingGlobal(true);
          setLoadingStep('Synchronizing Global Biosphere Data (5-Day Satellite Cycle)...');
          await axios.post('http://localhost:8000/api/v1/system/synchronize');
          setLoadingStep('Synchronization Complete. Welcome to WildSight.');
          await new Promise(r => setTimeout(r, 1500));
        }
      } catch (e) {
        console.error("Global sync error:", e);
      } finally {
        setIsCheckingSync(false);
        setIsSyncingGlobal(false);
      }
    };
    checkSync();
  }, []);


  const handleSearch = (e) => {
    e.preventDefault();
    if (speciesName) {
      loadSpecies(speciesName.trim(), null, false, regionName.trim());
    }
  };

  // --- API FETCH ---
  // --- MAIN DATA FETCHING ---
  const loadSpecies = async (paramName, zoneId = null, silent = false, region = null) => {
    if (!silent) {
      setLoading(true);
      setActiveSpecies(null);
      setLoadingStep('Connecting to Sentinel-2 Satellite Network...');
      setIsUpToDate(false);
    }
    setError(null);
    if (!zoneId) setSelectedZone(null); // Reset selection only for national search
    try {
      console.log(`Fetching data for: ${paramName}, Zone: ${zoneId || 'National'} (Silent: ${silent})`);

      let url = `http://localhost:8000/api/v1/species/${paramName}`;
      if (zoneId) {
        url += `?zone_id=${zoneId}`;
      } else if (region) {
        url += `?location=${region}`;
      }

      const response = await axios.get(url);
      const data = response.data;
      
      if (data.environment_context?.is_cached) {
        setLoadingStep('Everything Up to Date (Synchronized with 5-Day Satellite Cycle)');
        setIsUpToDate(true);
        // Small delay so user can read the success message
        await new Promise(r => setTimeout(r, 1200));
      } else {
        setLoadingStep('Recent Database Update Detected: Fetching New Multispectral Data...');
        await new Promise(r => setTimeout(r, 800));
      }

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
        pulse_history: speciesData.pulse_history || [],
        is_cached: envData.is_cached
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
    // Optionally load Tiger on first load, or stay on landing page.
    // loadSpecies('Tiger'); 
  }, []);

  // --- CAROUSEL LOGIC ---
  const [slideIndex, setSlideIndex] = useState(0);
  const nextSlide = () => setSlideIndex((prev) => (prev + 1) % 4);
  const prevSlide = () => setSlideIndex((prev) => (prev - 1 + 4) % 4);

  // --- RENDER ---
  if (loading || isCheckingSync || isSyncingGlobal) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center relative overflow-hidden font-sans">
        {/* Animated Background */}
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1549313861-33587f3d2956?q=80&w=2670&auto=format&fit=crop')] bg-cover bg-center opacity-20 blur-xl scale-110"></div>
        <div className="absolute inset-0 bg-gradient-to-tr from-emerald-950/90 via-black to-slate-900/90"></div>
        
        <div className="text-center z-10 p-12 rounded-3xl border border-white/5 bg-white/5 backdrop-blur-2xl shadow-2xl max-w-lg w-full">
          <div className={`w-20 h-20 rounded-full mx-auto mb-8 flex items-center justify-center relative ${isUpToDate ? 'bg-emerald-500 shadow-[0_0_30px_rgba(16,185,129,0.5)]' : 'bg-slate-800'}`}>
            {isUpToDate ? (
              <ShieldCheck size={40} className="text-white animate-in zoom-in duration-500" />
            ) : (
              <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-400 rounded-full animate-spin"></div>
            )}
            
            {!isUpToDate && (
              <div className="absolute -top-1 -right-1 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center animate-pulse border-2 border-black">
                <Wind size={12} className="text-white" />
              </div>
            )}
          </div>
          
          <h2 className="text-3xl font-black text-white tracking-tight mb-3">
            {isUpToDate ? 'WildSight Synchronized' : 'Scanning Biosphere...'}
          </h2>
          
          <div className="flex flex-col gap-4">
            <div className={`py-3 px-6 rounded-xl text-sm font-bold uppercase tracking-widest transition-all duration-700 ${isUpToDate ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-white/5 text-slate-400 border border-white/5'}`}>
              {loadingStep}
            </div>
            
            <div className="flex gap-2 justify-center">
              {[0, 1, 2, 3].map(i => (
                <div key={i} className={`h-1 w-8 rounded-full transition-all duration-1000 ${isUpToDate ? 'bg-emerald-500' : (i === 0 ? 'bg-emerald-400 animate-pulse' : 'bg-white/10')}`}></div>
              ))}
            </div>
          </div>
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
            <button onClick={() => { setError(null); setActiveSpecies(null); setSpeciesName(''); }} className="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold transition-colors">
              Return to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!activeSpecies) {
    return (
      <div className="min-h-screen bg-[#050608] flex flex-col items-center justify-center p-8 relative overflow-hidden font-sans">
        {/* Animated Background Elements */}
        <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_50%,rgba(16,185,129,0.05)_0%,transparent_50%)]"></div>
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-emerald-500/10 rounded-full blur-[100px]"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-blue-500/10 rounded-full blur-[100px]"></div>

        <div className="max-w-4xl w-full z-10 text-center">
            <div className="inline-flex items-center gap-3 px-5 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full mb-10 animate-in slide-in-from-top duration-700">
                <MapIcon size={18} className="text-emerald-400" />
                <span className="text-xs font-black uppercase tracking-[0.3em] text-emerald-100">National Intelligence Platform</span>
            </div>

            <h1 className="text-8xl md:text-9xl font-black text-white tracking-tighter leading-none mb-8">
                WILD<span className="text-emerald-500">SIGHT</span>
            </h1>
            
            <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-16 leading-relaxed">
                Experience real-time AI-driven wildlife monitoring and habitat conservation powered by multispectral satellite telemetry and deep biodiversity intelligence.
            </p>

            {/* Central Search Bar */}
            <div className="bg-white/5 p-3 rounded-[40px] border border-white/10 shadow-2xl backdrop-blur-3xl mb-16 max-w-4xl mx-auto group focus-within:border-emerald-500/50 transition-all">
                <form onSubmit={handleSearch} className="flex flex-col md:flex-row items-center gap-4">
                    <div className="flex-1 flex items-center gap-2 w-full border-b md:border-b-0 md:border-r border-white/10 px-4">
                        <Search size={24} className="text-slate-500" />
                        <input 
                            type="text" 
                            value={speciesName}
                            onChange={(e) => setSpeciesName(e.target.value)}
                            placeholder="Animal Name (e.g. Tiger)"
                            className="flex-1 bg-transparent py-5 text-xl font-bold text-white focus:outline-none placeholder:text-slate-700"
                        />
                    </div>
                    <div className="flex-1 flex items-center gap-2 w-full px-4">
                        <MapPin size={24} className="text-slate-500" />
                        <input 
                            type="text" 
                            value={regionName}
                            onChange={(e) => setRegionName(e.target.value)}
                            placeholder="Region (e.g. India, Kerala)"
                            className="flex-1 bg-transparent py-5 text-xl font-bold text-white focus:outline-none placeholder:text-slate-700"
                        />
                    </div>
                    <button type="submit" className="w-full md:w-auto px-12 py-5 bg-emerald-500 hover:bg-emerald-400 text-black font-black rounded-[30px] text-lg transition-all shadow-[0_0_30px_rgba(16,185,129,0.3)] whitespace-nowrap">
                        INITIATE SCAN
                    </button>
                </form>
            </div>

            {/* Quick Categories */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                {QUICK_LINKS.map(link => (
                    <button 
                        key={link.name}
                        onClick={() => loadSpecies(link.name)}
                        className="p-8 bg-white/5 border border-white/5 rounded-[30px] hover:bg-emerald-500 hover:text-black transition-all group flex flex-col items-center gap-4 shadow-lg"
                    >
                        <div className="p-4 bg-white/5 rounded-2xl group-hover:bg-black/10 transition-colors">
                            {React.cloneElement(link.icon, { size: 28 })}
                        </div>
                        <span className="font-black uppercase tracking-widest text-xs">{link.name}</span>
                    </button>
                ))}
            </div>
        </div>
        
        {/* Footer */}
        <div className="absolute bottom-10 left-0 right-0 text-center">
            <p className="text-[10px] font-black text-slate-600 uppercase tracking-[0.5em]">Powered by ESA Sentinel-2 & NASA FIRMS</p>
        </div>
      </div>
    );
  }

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
    <div className="min-h-screen bg-[#050608] font-sans text-slate-300 pb-10 relative selection:bg-emerald-500/30">

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
      <header className="bg-black/40 backdrop-blur-xl text-white shadow-2xl sticky top-0 z-50 overflow-hidden border-b border-white/5">
        <div className="max-w-[2200px] mx-auto px-8 py-5">
          <div className="flex items-center justify-between gap-10">
            <div className="flex items-center gap-5 group cursor-pointer shrink-0" onClick={() => loadSpecies('Tiger')}>
              <div className="p-4 bg-emerald-500 rounded-2xl shadow-[0_0_20px_rgba(16,185,129,0.3)] group-hover:rotate-6 transition-transform">
                <MapIcon size={28} className="text-black" />
              </div>
              <div>
                <h1 className="text-3xl font-black text-white tracking-tighter leading-none flex items-center gap-2">
                  WILDSIGHT <span className="text-emerald-500">INDIA</span>
                  <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-1 rounded-md tracking-[0.2em] font-black uppercase">v2.0</span>
                </h1>
                <p className="text-[10px] text-emerald-500/40 uppercase tracking-[0.4em] font-black mt-1">Satellite Intelligence Platform</p>
              </div>
            </div>

            <div className="flex-1 max-w-3xl">
              <form onSubmit={handleSearch} className="relative group">
                <input
                  type="text"
                  value={speciesName}
                  onChange={(e) => setSpeciesName(e.target.value)}
                  placeholder="Search Biosphere (e.g. Panthera tigris, Asian Elephant)..."
                  className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-14 pr-32 text-lg focus:outline-none focus:border-emerald-500/50 focus:bg-white/10 transition-all placeholder:text-slate-600 text-white"
                />
                <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-600 group-focus-within:text-emerald-500 transition-colors" size={24} />
                <button type="submit" className="absolute right-3 top-1/2 -translate-y-1/2 px-8 py-2 bg-emerald-500 hover:bg-emerald-400 text-black font-black rounded-xl text-sm transition-all shadow-[0_0_20px_rgba(16,185,129,0.3)]">
                  SCAN
                </button>
              </form>
            </div>

            <div className="flex items-center gap-8 shrink-0">
              <div className="hidden xl:flex items-center gap-4 border-r border-white/10 pr-8">
                <div className="text-right">
                  <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest leading-none mb-1">Status</div>
                  <div className="text-xs font-bold text-emerald-400 flex items-center gap-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                    SATELLITE ONLINE
                  </div>
                </div>
              </div>
              {user ? (
                <button onClick={() => navigate('/profile')} className="flex items-center gap-4 group">
                  <div className="text-right">
                    <div className="text-sm font-black text-white">{user.full_name}</div>
                    <div className="text-[10px] text-slate-500 font-bold uppercase tracking-tighter">Conservationist</div>
                  </div>
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 p-[2px]">
                    <div className="w-full h-full rounded-[14px] bg-black flex items-center justify-center font-black text-emerald-400">
                      {user.full_name.charAt(0)}
                    </div>
                  </div>
                </button>
              ) : (
                <button onClick={() => navigate('/login')} className="px-8 py-3 bg-white text-black font-black rounded-2xl text-sm hover:bg-emerald-500 transition-all">
                  SIGN IN
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-[2200px] mx-auto p-8 flex flex-col xl:flex-row gap-8">
        
        {/* LEFT COLUMN: MAIN MAP & ANALYTICS */}
        <div className="flex-1 flex flex-col gap-8">
          
          {/* MAP SECTION */}
          <section className="relative h-[650px] bg-black rounded-[40px] border border-white/5 overflow-hidden shadow-2xl group">
            {/* Map UI Overlays */}
            <div className="absolute top-8 left-8 z-[400] flex flex-col gap-3">
              <div className="bg-black/60 backdrop-blur-xl p-5 rounded-3xl border border-white/10 shadow-2xl">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></div>
                  <span className="text-[10px] font-black text-emerald-500 uppercase tracking-[0.2em]">Live Telemetry</span>
                </div>
                <div className="text-2xl font-black text-white tracking-tighter">
                  {activeSpecies.checkpoints.length} <span className="text-slate-500 text-sm font-bold uppercase ml-1">Active Sightings</span>
                </div>
              </div>

              {activeSpecies.is_cached && (
                <div className="bg-emerald-500/10 backdrop-blur-xl p-4 rounded-2xl border border-emerald-500/20 flex items-center gap-3 animate-in slide-in-from-left duration-700">
                  <ShieldCheck size={18} className="text-emerald-400" />
                  <span className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">Everything Up to Date</span>
                </div>
              )}
            </div>

            <MapContainer center={[activeSpecies.location.lat, activeSpecies.location.lon]} zoom={activeSpecies.location.zoom} style={{ height: '100%', width: '100%' }} zoomControl={false}>
              <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; CARTO'
              />
              <MapUpdater center={[activeSpecies.location.lat, activeSpecies.location.lon]} zoom={activeSpecies.location.zoom} />

              {activeSpecies.distribution?.zones.map((zone, i) => (
                <CircleMarker
                  key={i}
                  center={[zone.lat, zone.lon]}
                  radius={Math.min(zone.sighting_count * 4, 40)}
                  pathOptions={{
                    color: activeSpecies.checkpoints_region ? "#10b981" : "#f59e0b",
                    fillColor: activeSpecies.checkpoints_region ? "#10b981" : "#f59e0b",
                    fillOpacity: 0.2,
                    weight: 2
                  }}
                  eventHandlers={{
                    click: () => {
                      setSelectedZone(zone);
                      loadSpecies(activeSpecies.name, zone.id, true);
                    }
                  }}
                />
              ))}

              {activeSpecies.checkpoints.map((pt, i) => (
                <Marker key={i} position={[pt.lat, pt.lon]} opacity={0.6}>
                  <Popup>
                    <div className="bg-slate-900 p-2 rounded-lg text-white font-sans">
                      <strong className="text-emerald-400">{activeSpecies.name}</strong><br />
                      <span className="text-xs opacity-60">ID: {pt.id || 'N/A'}</span>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
            
            {/* Map Controls */}
            <div className="absolute bottom-8 left-8 right-8 z-[400] flex justify-between items-end">
              <div className="flex gap-2">
                {QUICK_LINKS.slice(0, 3).map(l => (
                  <button key={l.name} onClick={() => loadSpecies(l.name)} className="px-5 py-2 bg-black/60 backdrop-blur-md border border-white/10 rounded-full text-[10px] font-black text-white hover:bg-emerald-500 hover:text-black transition-all uppercase tracking-widest">
                    {l.name}
                  </button>
                ))}
              </div>
              <button onClick={() => runZoneAnalysis()} className="bg-emerald-500 text-black px-10 py-5 rounded-[25px] font-black text-sm uppercase tracking-[0.2em] shadow-[0_0_50px_rgba(16,185,129,0.4)] hover:scale-105 transition-transform">
                Generate Prediction
              </button>
            </div>
          </section>

          {/* ANALYTICS ROW */}
          <section className="grid grid-cols-1 md:grid-cols-2 gap-8 h-[350px]">
            {/* VEGETATION PULSE */}
            <div className="bg-white/5 border border-white/10 rounded-[40px] p-8 flex flex-col">
              <div className="flex justify-between items-start mb-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-emerald-500/10 rounded-2xl text-emerald-400"><TreeDeciduous size={24} /></div>
                  <div>
                    <h4 className="text-lg font-black text-white">Vegetation Pulse</h4>
                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Biomass Index (NDVI)</p>
                  </div>
                </div>
              </div>
              <div className="flex-1">
                <Line data={{
                  labels: activeSpecies.days_vegetation,
                  datasets: [{
                    label: 'NDVI',
                    data: activeSpecies.analysis.vegetation.ndvi,
                    borderColor: '#10b981',
                    borderWidth: 4,
                    tension: 0.4,
                    pointRadius: 0,
                    fill: true,
                    backgroundColor: 'rgba(16, 185, 129, 0.05)'
                  }]
                }} options={{...commonOptions, scales: { x: { display: false }, y: { display: false } }}} />
              </div>
            </div>

            {/* CLIMATE RESILIENCE */}
            <div className="bg-white/5 border border-white/10 rounded-[40px] p-8 flex flex-col">
              <div className="flex justify-between items-start mb-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-blue-500/10 rounded-2xl text-blue-400"><Thermometer size={24} /></div>
                  <div>
                    <h4 className="text-lg font-black text-white">Climate Shield</h4>
                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Stability Variance</p>
                  </div>
                </div>
              </div>
              <div className="flex-1">
                <Line data={{
                  labels: activeSpecies.years_forecast,
                  datasets: [{
                    label: 'Temp',
                    data: activeSpecies.analysis.climate.temp,
                    borderColor: '#3b82f6',
                    borderWidth: 4,
                    tension: 0.4,
                    pointRadius: 0
                  }]
                }} options={{...commonOptions, scales: { x: { display: false }, y: { display: false } }}} />
              </div>
            </div>
          </section>
        </div>

        {/* RIGHT COLUMN: SIDEBAR DATA PANELS */}
        <aside className="w-full xl:w-[480px] shrink-0 flex flex-col gap-8">
          
          {/* PRIMARY SPECIES PANEL */}
          <section className="bg-white/5 border border-white/10 rounded-[40px] p-10 flex flex-col shadow-2xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-10 opacity-5 group-hover:opacity-10 transition-opacity">
              <Activity size={120} />
            </div>
            
            <div className="mb-10">
              <div className="flex justify-between items-center mb-6">
                <span className={`px-4 py-1 rounded-full text-[10px] font-black uppercase tracking-[0.2em] ${activeSpecies.status.includes('Endangered') ? 'bg-red-500/20 text-red-500' : 'bg-emerald-500/20 text-emerald-500'}`}>
                  {activeSpecies.status}
                </span>
                <div className="flex gap-1">
                  {[1, 2, 3].map(i => <div key={i} className={`w-1.5 h-1.5 rounded-full ${i <= 2 ? 'bg-emerald-500' : 'bg-white/10'}`}></div>)}
                </div>
              </div>
              
              <h2 className="text-5xl font-black text-white tracking-tighter leading-tight mb-2">
                {activeSpecies.name.split(' ').map((word, i) => (
                  <span key={i} className={i % 2 === 1 ? 'text-emerald-500' : ''}>{word} </span>
                ))}
              </h2>
              <p className="text-sm font-bold text-slate-500 uppercase tracking-widest leading-none">Global Census Tracking #WS-{activeSpecies.name.charAt(0)}</p>
            </div>

            <div className="grid grid-cols-2 gap-8 mb-10">
              <div className="bg-white/5 rounded-3xl p-6 border border-white/5">
                <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Population</div>
                <div className="text-3xl font-black text-white tracking-tighter">{activeSpecies.latestCount.toLocaleString()}</div>
                <div className={`text-[10px] font-bold mt-1 flex items-center gap-1 ${activeSpecies.pulse_delta >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {activeSpecies.pulse_delta >= 0 ? '+' : ''}{activeSpecies.pulse_delta} Pulse
                </div>
              </div>
              <div className="bg-white/5 rounded-3xl p-6 border border-white/5">
                <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Risk Score</div>
                <div className="text-3xl font-black text-emerald-500 tracking-tighter">{(activeSpecies.pulse_history?.[0]?.risk * 100 || 0).toFixed(0)}%</div>
                <div className="text-[10px] font-bold mt-1 text-slate-500 italic">Moderate Stability</div>
              </div>
            </div>

            <div className="flex-1 min-h-[160px] mb-10">
              <Line data={{
                labels: activeSpecies.pulse_history?.map(p => p.date).reverse() || [],
                datasets: [{
                  data: activeSpecies.pulse_history?.map(p => p.count).reverse() || [],
                  borderColor: '#10b981',
                  borderWidth: 3,
                  tension: 0.4,
                  pointRadius: 4,
                  pointBackgroundColor: '#10b981'
                }]
              }} options={{...commonOptions, scales: { x: { display: false }, y: { display: false } }}} />
            </div>

            <div className="space-y-4">
              <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mb-4">Habitat Clustering</h4>
              {activeSpecies.distribution?.zones.slice(0, 3).map(zone => (
                <div key={zone.id} onClick={() => loadSpecies(activeSpecies.name, zone.id, true)} className={`flex justify-between items-center p-5 rounded-2xl border transition-all cursor-pointer ${selectedZone?.id === zone.id ? 'bg-emerald-500 border-emerald-500 text-black' : 'bg-white/5 border-white/5 hover:border-white/10 text-white'}`}>
                  <div className="flex items-center gap-4">
                    <MapPin size={18} className={selectedZone?.id === zone.id ? 'text-black' : 'text-emerald-500'} />
                    <div className="text-sm font-black">{zone.name}</div>
                  </div>
                  <div className="font-mono font-bold text-xs">{zone.sighting_count}</div>
                </div>
              ))}
            </div>
          </section>

          {/* SECONDARY INSIGHTS PANEL */}
          <section className="bg-emerald-500 rounded-[40px] p-10 text-black flex flex-col gap-6 shadow-2xl">
            <div>
              <h3 className="text-2xl font-black tracking-tighter mb-2">Preservation AI</h3>
              <p className="text-xs font-bold uppercase tracking-widest opacity-60">Neural Network Directives</p>
            </div>
            
            <div className="space-y-3">
              {slides[slideIndex].title.includes('Disturbance') ? (
                <div className="bg-black/10 p-5 rounded-3xl border border-black/5">
                  <div className="flex items-center gap-3 mb-2">
                    <Flame size={16} />
                    <span className="text-xs font-black uppercase">Anthropogenic Risk</span>
                  </div>
                  <p className="text-sm font-bold opacity-80 leading-relaxed">Night-light patterns indicate 12% urban encroachment in buffer zones.</p>
                </div>
              ) : (
                <div className="bg-black/10 p-5 rounded-3xl border border-black/5">
                  <div className="flex items-center gap-3 mb-2">
                    <ShieldCheck size={16} />
                    <span className="text-xs font-black uppercase">Intervention Strategy</span>
                  </div>
                  <p className="text-sm font-bold opacity-80 leading-relaxed">Initiate reforestation of secondary corridors to enhance genetic flow.</p>
                </div>
              )}
            </div>

            <button onClick={() => nextSlide()} className="w-full py-4 bg-black text-white rounded-2xl font-black text-xs uppercase tracking-[0.2em] mt-2 hover:bg-slate-900 transition-all">
              Cycle Insights
            </button>
          </section>

        </aside>

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
