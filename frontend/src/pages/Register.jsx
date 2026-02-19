import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { auth } from '../firebase';
import { createUserWithEmailAndPassword, updateProfile, GoogleAuthProvider, signInWithPopup } from 'firebase/auth';
import { User, Mail, Lock, ArrowRight, ShieldCheck, MapPin, Navigation } from 'lucide-react';

const Register = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        full_name: '',
        email: '',
        password: '',
        latitude: null,
        longitude: null,
    });
    const [loading, setLoading] = useState(false);
    const [locLoading, setLocLoading] = useState(false);
    const [error, setError] = useState('');

    const detectLocation = () => {
        setLocLoading(true);
        if (!navigator.geolocation) {
            setError("Geolocation is not supported by your browser.");
            setLocLoading(false);
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                setFormData(prev => ({
                    ...prev,
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                }));
                setLocLoading(false);
            },
            (err) => {
                setError("Unable to retrieve location. Please grant permission.");
                setLocLoading(false);
            }
        );
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        if (!formData.latitude || !formData.longitude) {
            setError("Please detect your location for urgent alerts.");
            setLoading(false);
            return;
        }

        try {
            // 1. Firebase Auth
            const userCredential = await createUserWithEmailAndPassword(auth, formData.email, formData.password);
            const user = userCredential.user;
            await updateProfile(user, { displayName: formData.full_name });

            // 2. Sync with Backend & Get ID Token
            const token = await user.getIdToken();
            await axios.post('http://localhost:8000/api/v1/auth/register', {
                email: formData.email,
                full_name: formData.full_name,
                latitude: formData.latitude,
                longitude: formData.longitude,
                firebase_uid: user.uid
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });

            localStorage.setItem('wildsight_token', token);
            navigate('/');
        } catch (err) {
            console.error("Firebase Auth Error:", err);
            const backendMsg = err.response?.data?.detail
                ? JSON.stringify(err.response.data.detail)
                : (err.message || 'Registration failed.');
            setError(`Error: ${backendMsg}`);
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleSignIn = async () => {
        setLoading(true);
        setError('');

        if (!formData.latitude || !formData.longitude) {
            setError("Please detect your location first.");
            setLoading(false);
            return;
        }

        try {
            const provider = new GoogleAuthProvider();
            const result = await signInWithPopup(auth, provider);
            const user = result.user;

            const token = await user.getIdToken();
            await axios.post('http://localhost:8000/api/v1/auth/register', {
                email: user.email,
                full_name: user.displayName,
                latitude: formData.latitude,
                longitude: formData.longitude,
                firebase_uid: user.uid
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });

            localStorage.setItem('wildsight_token', token);
            navigate('/');
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-emerald-600/10 rounded-full blur-[120px] pointer-events-none"></div>
            <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none"></div>

            <div className="max-w-md w-full z-10">
                <div className="text-center mb-10">
                    <div className="inline-flex p-4 bg-emerald-500/10 rounded-3xl mb-4 border border-emerald-500/20">
                        <ShieldCheck className="text-emerald-400" size={32} />
                    </div>
                    <h1 className="text-4xl font-black text-white tracking-tight">Join <span className="text-emerald-400">WildSight</span></h1>
                    <p className="text-slate-400 mt-2">Get automated AI alerts for endangered species in your area.</p>
                </div>

                <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700 p-8 rounded-3xl shadow-2xl">
                    <form onSubmit={handleRegister} className="space-y-4">
                        {error && (
                            <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-xl text-center font-bold">
                                {error}
                            </div>
                        )}

                        <div className="space-y-1">
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-widest ml-1">Full Name</label>
                            <div className="relative">
                                <User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                                <input
                                    type="text"
                                    required
                                    value={formData.full_name}
                                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                                    className="w-full bg-slate-900/50 border border-slate-700 rounded-2xl py-4 pl-12 pr-4 text-white focus:outline-none focus:border-emerald-500/50 transition-all font-medium"
                                    placeholder="John Doe"
                                />
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-widest ml-1">Email Address</label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                                <input
                                    type="email"
                                    required
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    className="w-full bg-slate-900/50 border border-slate-700 rounded-2xl py-4 pl-12 pr-4 text-white focus:outline-none focus:border-emerald-500/50 transition-all font-medium"
                                    placeholder="john@example.com"
                                />
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-widest ml-1">Password</label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                                <input
                                    type="password"
                                    required
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    className="w-full bg-slate-900/50 border border-slate-700 rounded-2xl py-4 pl-12 pr-4 text-white focus:outline-none focus:border-emerald-500/50 transition-all font-medium"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        {/* Location Box */}
                        <div className="p-4 bg-slate-900/50 border border-slate-700 rounded-2xl space-y-3">
                            <div className="flex justify-between items-center">
                                <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-widest">
                                    <MapPin size={14} className="text-emerald-400" />
                                    Habitat Radius Monitoring
                                </div>
                                {formData.latitude && (
                                    <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full font-bold">READY</span>
                                )}
                            </div>

                            <button
                                type="button"
                                onClick={detectLocation}
                                disabled={locLoading}
                                className={`w-full py-2.5 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all border ${formData.latitude
                                    ? 'bg-slate-800 border-emerald-500/30 text-emerald-400'
                                    : 'bg-emerald-600/10 border-emerald-600/20 text-emerald-500 hover:bg-emerald-600/20'
                                    }`}
                            >
                                {locLoading ? (
                                    <div className="w-4 h-4 border-2 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin" />
                                ) : (
                                    <><Navigation size={14} /> {formData.latitude ? 'Location Captured' : 'Detect My Location'}</>
                                )}
                            </button>

                            {formData.latitude && (
                                <div className="flex gap-4 text-[10px] font-mono text-slate-500 justify-center">
                                    <span>LAT: {formData.latitude.toFixed(4)}</span>
                                    <span>LON: {formData.longitude.toFixed(4)}</span>
                                </div>
                            )}
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-black py-4 rounded-2xl transition-all shadow-xl shadow-emerald-600/20 flex items-center justify-center gap-2 mt-2"
                        >
                            {loading ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <>START CONSERVING <ArrowRight size={20} /></>
                            )}
                        </button>

                        <div className="relative my-6 text-center">
                            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-700"></div></div>
                            <span className="relative px-4 bg-slate-900 text-slate-500 text-xs font-bold">OR</span>
                        </div>

                        <button
                            type="button"
                            onClick={handleGoogleSignIn}
                            className="w-full bg-white text-slate-900 py-3.5 rounded-2xl font-bold flex items-center justify-center gap-3 hover:bg-slate-50 transition-all border border-slate-300"
                        >
                            <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" className="w-5 h-5" alt="google" />
                            Continue with Google
                        </button>
                    </form>

                    <div className="mt-8 text-center text-slate-500 text-sm">
                        Already have an account? <Link to="/login" className="text-emerald-400 font-bold hover:underline">Log In</Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Register;
