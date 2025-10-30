// src/pages/HomePage.jsx

import React, { useState, useEffect } from 'react';
import { useInterviewSession } from '../hooks/useInterviewSession'; 
import { registerUser, fetchRoles, fetchLevels } from '../services/api';
import Dropdown from '../components/common/Dropdown';
import Button from '../components/common/Button';
import FeatureIcon from '../components/common/FeatureIcon'; 

// Ikon menggunakan inline SVG (diambil dari Lucide)
const IconSparkles = (props) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9.9 14.9L2 17.5l7.9 2.6V22l2.6-7.1L15.1 22l2.6-7.1L22 17.5l-7.9-2.6L12.5 8 9.9 14.9z"/><path d="M12.5 8L15 1 17.5 8" /></svg>
);
const IconMessageSquare = (props) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
);
const IconZap = (props) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
);


const HomePage = () => {
    const [name, setName] = useState('');
    const [roles, setRoles] = useState([]);
    const [levels, setLevels] = useState([]);
    const [selectedRoleId, setSelectedRoleId] = useState(null); 
    const [selectedLevelId, setSelectedLevelId] = useState(null);

    const [alertMessage, setAlertMessage] = useState(null); 
    const [isRegistering, setIsRegistering] = useState(false);
    const { loading, setLoading, error, setError, handleStartSession } = useInterviewSession(); 

    const showAlert = (message) => {
        setAlertMessage(message);
        setTimeout(() => setAlertMessage(null), 4000); 
    };

    useEffect(() => {
        const loadData = async () => {
            try {
                const [rolesData, levelsData] = await Promise.all([fetchRoles(), fetchLevels()]);
                setRoles(rolesData);
                setLevels(levelsData);

                // Set nilai default ke item pertama jika data tersedia
                if (rolesData.length > 0) setSelectedRoleId(rolesData[0].id);
                if (levelsData.length > 0) setSelectedLevelId(levelsData[0].id);

            } catch (err) {
                console.error("Gagal memuat data roles/levels:", err);
                setError("Gagal memuat pilihan Role/Level dari server.");
            }
        };
        loadData();
    }, [setError]);


    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        if (!name || !selectedRoleId || !selectedLevelId) {
            showAlert("Mohon isi Nama, Posisi Pekerjaan, dan Level dengan lengkap.");
            return;
        }

        setIsRegistering(true);
        setLoading(true);

        try {
            const userRegistrationResponse = await registerUser(name, selectedRoleId, selectedLevelId);
            const userId = userRegistrationResponse.user_id;

            const roleName = roles.find(r => r.id === selectedRoleId)?.role_name;
            const levelName = levels.find(l => l.id === selectedLevelId)?.level_name;

            if (!roleName || !levelName) {
                throw new Error("Pilihan Role atau Level tidak valid.");
            }

            handleStartSession(roleName, levelName, userId, selectedRoleId, selectedLevelId);

        } catch (err) {
            console.error("Gagal mendaftar atau memulai sesi:", err);
            const backendDetail = err.response?.data?.detail;
            setError(backendDetail || err.message || "Terjadi kesalahan saat memulai sesi.");
            setLoading(false);
        } finally {
            setIsRegistering(false);
        }
    };

    const isFormIncomplete = !name || !selectedRoleId || !selectedLevelId;
    const isProcessing = loading || isRegistering;

    return (
        // Latar Belakang Keseluruhan: Sedikit gradien atau warna solid terang
        <div className="min-h-screen flex justify-center items-center bg-gradient-to-br from-blue-50 to-white p-4 font-inter">
            
            {/* Kontainer Card Utama: Lebih besar, shadow lebih kuat, rounded lebih besar */}
            <div className="flex max-w-6xl w-full mx-auto bg-white rounded-3xl shadow-2xl-custom overflow-hidden">
                
                {/* KOLOM KIRI: FORMULIR */}
                <div className="lg:w-1/2 w-full p-8 md:p-12 space-y-6">
                    
                    {/* Header Kecil "Powered by AI Gemini" */}
                    <div className="flex items-center text-sm font-bold bg-blue-50 rounded-full px-4 py-2 w-fit text-gray-700">
                        <IconSparkles className="w-4 h-4 mr-2 fill-blue-500 text-blue-500" />
                        Powered by AI Gemini
                    </div>

                    {/* Judul Besar */}
                    <header>
                        <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 leading-tight">
                            AI Interview Simulation
                        </h1>
                        <p className="mt-3 text-gray-600 text-lg max-w-md">
                            Latih wawancaramu dengan kecerdasan buatan — dapatkan pertanyaan dan feedback otomatis.
                        </p>
                    </header>

                    {/* Form Input */}
                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-1">Nama</label>
                            <input
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="Masukkan nama Anda..."
                                className="block w-full border border-gray-200 rounded-xl shadow-inner p-3 focus:ring-blue-500 focus:border-blue-500 transition duration-150 text-gray-800"
                                disabled={isProcessing}
                            />
                        </div>

                        <Dropdown
                            label="Pilih Posisi Pekerjaan"
                            placeholder="Pilih posisi yang kamu inginkan..."
                            options={roles}
                            selectedId={selectedRoleId}
                            setSelectedId={setSelectedRoleId}
                            idKey="id"
                            nameKey="role_name"
                            disabled={isProcessing}
                        />

                        <Dropdown
                            label="Pilih Level"
                            placeholder="Pilih level pengalaman..."
                            options={levels}
                            selectedId={selectedLevelId}
                            setSelectedId={setSelectedLevelId}
                            idKey="id"
                            nameKey="level_name"
                            disabled={isProcessing}
                        />

                        <Button type="submit" disabled={isProcessing || isFormIncomplete}>
                            {isProcessing ? (
                                <span className="flex items-center justify-center">
                                    <svg className="animate-spin h-5 w-5 mr-3 text-white" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
                                    Memproses...
                                </span>
                            ) : (
                                "Mulai Wawancara"
                            )}
                        </Button>
                    </form>

                    {/* Area Ikon Fitur */}
                    <div className="flex justify-around items-center pt-4 border-t border-gray-100 mt-6 -mx-3">
                        <FeatureIcon 
                            icon={<IconSparkles className="w-6 h-6" />}
                            title="AI Powered"
                        />
                        <FeatureIcon 
                            icon={<IconMessageSquare className="w-6 h-6" />}
                            title="Real Feedback"
                        />
                        <FeatureIcon 
                            icon={<IconZap className="w-6 h-6" />}
                            title="Instant Results"
                        />
                    </div>
                </div>

                {/* KOLOM KANAN: GAMBAR ROBOT */}
                <div className="hidden lg:flex lg:w-1/2 bg-blue-50/70 p-8 justify-center items-center rounded-r-3xl relative">
                    <img 
                        src="https://placehold.co/600x800/e0e7ff/225c9b?text=AI+Robot+Interviewer"
                        alt="Robot AI untuk Wawancara" 
                        className="max-w-full max-h-full object-contain p-4"
                        onError={(e) => { e.target.onerror = null; e.target.src = "https://placehold.co/600x800/e0e7ff/225c9b?text=AI+Robot+Interviewer"; }}
                    />
                </div>
            </div>

            {alertMessage && (
                <div className="fixed top-4 right-4 bg-red-600 text-white p-3 rounded-xl shadow-xl transition-opacity duration-300 z-50">
                    {alertMessage}
                </div>
            )}
            {error && !alertMessage && (
                 <div className="fixed top-4 right-4 bg-red-600 text-white p-3 rounded-xl shadow-xl transition-opacity duration-300 z-50">
                    {error}
                </div>
            )}
        </div>
    );
};

export default HomePage;