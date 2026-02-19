import React, { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { auth } from '../firebase';
import { signInWithEmailAndPassword, GoogleAuthProvider, signInWithPopup } from 'firebase/auth';
import { Mail, Lock, ArrowRight, LogIn } from 'lucide-react';

const Login = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const successMessage = location.state?.message;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        // DEV MODE BYPASS
        if (formData.email === 'dev@wildsight.ai') {
            console.warn("DEV MODE: Bypassing Firebase Auth");
            localStorage.setItem('wildsight_token', 'dev-bypass-token-' + Date.now());
            // Simulate network delay for realism
            setTimeout(() => {
                setLoading(false);
                navigate('/');
            }, 800);
            return;
        }

        try {
            const userCredential = await signInWithEmailAndPassword(auth, formData.email, formData.password);
            const token = await userCredential.user.getIdToken();
            localStorage.setItem('wildsight_token', token);
            navigate('/');
        } catch (err) {
            console.error("Login Error:", err);
            if (err.code === 'auth/operation-not-allowed') {
                setError('Email/Password login is not enabled in Firebase Console. Use dev@wildsight.ai to bypass.');
            } else {
                setError(err.message || 'Invalid email or password.');
            }
        } finally {
            if (formData.email !== 'dev@wildsight.ai') {
                setLoading(false);
            }
        }
    };

    const handleGoogleSignIn = async () => {
        setLoading(true);
        setError('');
        try {
            const provider = new GoogleAuthProvider();
            const result = await signInWithPopup(auth, provider);
            const token = await result.user.getIdToken();
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

            <div className="max-w-md w-full z-10">
                <div className="text-center mb-10">
                    <div className="inline-flex p-4 bg-emerald-500/10 rounded-3xl mb-4 border border-emerald-500/20">
                        <LogIn className="text-emerald-400" size={32} />
                    </div>
                    <h1 className="text-4xl font-black text-white tracking-tight">Welcome Back</h1>
                    <p className="text-slate-400 mt-2">Sign in to manage your AI conservation alerts.</p>
                </div>

                <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700 p-8 rounded-3xl shadow-2xl">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {successMessage && (
                            <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm rounded-xl text-center font-bold">
                                {successMessage}
                            </div>
                        )}
                        {error && (
                            <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-xl text-center font-bold">
                                {error}
                            </div>
                        )}

                        <div className="space-y-1">
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-widest ml-1">Email Address</label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                                <input
                                    type="email"
                                    required
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    className="w-full bg-slate-900/50 border border-slate-700 rounded-2xl py-4 pl-12 pr-4 text-white focus:outline-none focus:border-emerald-500/50 transition-all"
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
                                    className="w-full bg-slate-900/50 border border-slate-700 rounded-2xl py-4 pl-12 pr-4 text-white focus:outline-none focus:border-emerald-500/50 transition-all"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-black py-4 rounded-2xl transition-all shadow-xl shadow-emerald-600/20 flex items-center justify-center gap-2 mt-4"
                        >
                            {loading ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <>SIGN IN <ArrowRight size={20} /></>
                            )}
                        </button>

                        <div className="relative my-4 text-center">
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
                        <button
                            type="button"
                            onClick={() => {
                                setFormData({ email: 'dev@wildsight.ai', password: 'dev' });
                                // Optional: auto-submit or just let them click
                            }}
                            className="w-full mt-2 text-xs font-bold text-emerald-500 hover:text-emerald-400 py-2 border border-emerald-500/30 rounded-xl hover:bg-emerald-500/10 transition-all uppercase tracking-wider"
                        >
                            Or use Dev Account (Bypass Auth)
                        </button>
                    </form>

                    <div className="mt-8 text-center text-slate-500 text-sm">
                        Don't have an account? <Link to="/register" className="text-emerald-400 font-bold hover:underline">Register Now</Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
