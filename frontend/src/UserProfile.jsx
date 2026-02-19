import React, { useState, useEffect } from 'react';
import {
    User,
    Mail,
    MapPin,
    Key,
    CreditCard,
    Copy,
    Check,
    Edit2,
    Save,
    ArrowLeft
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const UserProfile = () => {
    const navigate = useNavigate();
    const [isEditing, setIsEditing] = useState(false);
    const [copiedId, setCopiedId] = useState(false);
    const [copiedKey, setCopiedKey] = useState(false);

    // Initial State from API or Defaults
    const [profile, setProfile] = useState({
        firstName: '',
        lastName: '',
        email: '',
        country: 'India',
        userId: '',
    });

    useEffect(() => {
        const fetchProfile = async () => {
            const token = localStorage.getItem('wildsight_token');
            if (!token) {
                navigate('/login');
                return;
            }
            try {
                const res = await axios.get('http://localhost:8000/api/v1/auth/me', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                const data = res.data;
                const [first, ...last] = data.full_name.split(' ');
                setProfile({
                    firstName: first || '',
                    lastName: last.join(' ') || '',
                    email: data.email,
                    country: data.area_of_interest,
                    userId: data.id,
                    latitude: data.latitude,
                    longitude: data.longitude
                });
            } catch (e) {
                console.error("Profile fetch error:", e);
                localStorage.removeItem('wildsight_token');
                navigate('/login');
            }
        };
        fetchProfile();
    }, [navigate]);

    const handleSave = async () => {
        // Logic to update lat/lon if needed
        setIsEditing(false);
    };

    const handleLogout = async () => {
        try {
            const { auth: firebaseAuth } = await import('./firebase');
            await firebaseAuth.signOut();
            localStorage.removeItem('wildsight_token');
            navigate('/login');
        } catch (e) {
            console.error("Logout error:", e);
        }
    };

    const copyToClipboard = (text, type) => {
        navigator.clipboard.writeText(text);
        if (type === 'id') {
            setCopiedId(true);
            setTimeout(() => setCopiedId(false), 2000);
        } else {
            setCopiedKey(true);
            setTimeout(() => setCopiedKey(false), 2000);
        }
    };

    return (
        <div className="min-h-screen bg-slate-900 text-slate-100 flex items-center justify-center p-6">
            <div className="max-w-2xl w-full">

                {/* Header */}
                <div className="flex items-center gap-4 mb-8">
                    <button onClick={() => navigate('/')} className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400 hover:text-white">
                        <ArrowLeft size={24} />
                    </button>
                    <h1 className="text-3xl font-bold tracking-tight text-white">User Profile</h1>
                </div>

                <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-8 shadow-xl backdrop-blur-sm">

                    <div className="space-y-6">

                        {/* FIRST NAME */}
                        <div className="group relative">
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1 block">First Name</label>
                            <div className="relative">
                                <input
                                    type="text"
                                    disabled={!isEditing}
                                    value={profile.firstName}
                                    onChange={(e) => setProfile({ ...profile, firstName: e.target.value })}
                                    className={`w-full bg-slate-900/50 border ${isEditing ? 'border-emerald-500/50 focus:border-emerald-500' : 'border-slate-700'} rounded-xl px-4 py-3 text-slate-200 focus:outline-none transition-all`}
                                />
                                {!isEditing && <Edit2 size={16} className="absolute right-4 top-3.5 text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity" />}
                            </div>
                        </div>

                        {/* LAST NAME */}
                        <div className="group relative">
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1 block">Last Name</label>
                            <div className="relative">
                                <input
                                    type="text"
                                    disabled={!isEditing}
                                    value={profile.lastName}
                                    onChange={(e) => setProfile({ ...profile, lastName: e.target.value })}
                                    className={`w-full bg-slate-900/50 border ${isEditing ? 'border-emerald-500/50 focus:border-emerald-500' : 'border-slate-700'} rounded-xl px-4 py-3 text-slate-200 focus:outline-none transition-all`}
                                />
                            </div>
                        </div>

                        {/* EMAIL */}
                        <div className="group relative">
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1 block">Email</label>
                            <div className="relative">
                                <input
                                    type="email"
                                    disabled={!isEditing}
                                    value={profile.email}
                                    onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                                    className={`w-full bg-slate-900/50 border ${isEditing ? 'border-emerald-500/50 focus:border-emerald-500' : 'border-slate-700'} rounded-xl px-4 py-3 text-slate-200 focus:outline-none transition-all`}
                                />
                            </div>
                        </div>

                        {/* COUNTRY */}
                        <div className="group relative">
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1 block">Country</label>
                            <div className="relative">
                                <select
                                    disabled={!isEditing}
                                    value={profile.country}
                                    onChange={(e) => setProfile({ ...profile, country: e.target.value })}
                                    className={`w-full bg-slate-900/50 border ${isEditing ? 'border-emerald-500/50 focus:border-emerald-500' : 'border-slate-700'} rounded-xl px-4 py-3 text-slate-200 focus:outline-none transition-all appearance-none`}
                                >
                                    <option>India</option>
                                    <option>United States</option>
                                    <option>United Kingdom</option>
                                    <option>Canada</option>
                                    <option>Australia</option>
                                </select>
                            </div>
                        </div>

                        <div className="h-px bg-slate-700 my-8"></div>

                        {/* USER ID (READ ONLY) */}
                        <div>
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1 block">User ID</label>
                            <div className="relative flex items-center">
                                <code className="flex-1 bg-slate-900/80 border border-slate-700 rounded-xl px-4 py-3 text-slate-400 font-mono text-sm overflow-hidden text-ellipsis whitespace-nowrap">
                                    {profile.userId}
                                </code>
                                <button
                                    onClick={() => copyToClipboard(profile.userId, 'id')}
                                    className="ml-3 p-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl transition-colors text-slate-400 hover:text-white"
                                >
                                    {copiedId ? <Check size={18} className="text-emerald-500" /> : <Copy size={18} />}
                                </button>
                            </div>
                        </div>

                        {/* API KEY (READ ONLY) */}
                        <div>
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1 block">API Key</label>
                            <div className="relative flex items-center">
                                <code className="flex-1 bg-slate-900/80 border border-slate-700 rounded-xl px-4 py-3 text-slate-400 font-mono text-sm overflow-hidden text-ellipsis whitespace-nowrap">
                                    {profile.apiKey}
                                </code>
                                <button
                                    onClick={() => copyToClipboard(profile.apiKey, 'key')}
                                    className="ml-3 p-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl transition-colors text-slate-400 hover:text-white"
                                >
                                    {copiedKey ? <Check size={18} className="text-emerald-500" /> : <Copy size={18} />}
                                </button>
                            </div>
                        </div>

                        {/* FOOTER METADATA */}
                        <div className="pt-6 space-y-1">
                            <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">User Since: January 03, 2026</p>
                            <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Role: Account Admin</p>
                        </div>

                        {/* ACTIONS */}
                        <div className="pt-4 flex justify-center">
                            {isEditing ? (
                                <button
                                    onClick={handleSave}
                                    className="flex items-center gap-2 px-8 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg transition-all shadow-lg hover:shadow-emerald-500/20"
                                >
                                    <Save size={18} /> SAVE CHANGES
                                </button>
                            ) : (
                                <button
                                    onClick={() => setIsEditing(true)}
                                    className="flex items-center gap-2 px-8 py-3 bg-slate-700 hover:bg-slate-600 text-white font-bold rounded-lg transition-all border border-slate-600"
                                >
                                    <Edit2 size={18} /> EDIT PROFILE
                                </button>
                            )}
                            <button
                                onClick={handleLogout}
                                className="ml-4 flex items-center gap-2 px-8 py-3 bg-red-600/10 hover:bg-red-600/20 text-red-500 font-bold rounded-lg transition-all border border-red-500/20"
                            >
                                LOGOUT
                            </button>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );
};

export default UserProfile;
