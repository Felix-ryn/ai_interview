// src/pages/HomePage.jsx

import React, { useState, useEffect } from 'react';
// Pastikan useInterviewSession mengembalikan fungsi setLoading
import { useInterviewSession } from '../hooks/useInterviewSession'; 
// Import fungsi API yang baru
import { registerUser, fetchRoles, fetchLevels } from '../services/api';
import Dropdown from '../components/common/Dropdown';
import Button from '../components/common/Button';

const HomePage = () => {
    const [name, setName] = useState('');
    // State untuk menyimpan daftar Role dan Level dari API
    const [roles, setRoles] = useState([]);
    const [levels, setLevels] = useState([]);
    // 💡 PERBAIKAN: Set nilai awal ke null/undefined (atau -1) agar validasi berfungsi
    const [selectedRoleId, setSelectedRoleId] = useState(null); 
    const [selectedLevelId, setSelectedLevelId] = useState(null);

    const [isRegistering, setIsRegistering] = useState(false);
    // 💡 PERBAIKAN: Ambil setLoading dari hook
    const { loading, setLoading, error, setError, handleStartSession } = useInterviewSession(); 


    // 🟢 EFFECT: Mengambil data Role dan Level saat komponen dimuat
    useEffect(() => {
        const loadData = async () => {
            try {
                const [rolesData, levelsData] = await Promise.all([fetchRoles(), fetchLevels()]);
                setRoles(rolesData);
                setLevels(levelsData);

                // Set nilai default ke ID pertama jika ada
                // Ini memastikan dropdown memiliki nilai awal yang valid
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

        // 💡 PERBAIKAN: Validasi harus menggunakan !name, !selectedRoleId, dan !selectedLevelId
        // Tombol akan disabled jika salah satu null/undefined.
        if (!name || !selectedRoleId || !selectedLevelId) {
            alert("Mohon isi Nama, Role, dan Level dengan lengkap.");
            return;
        }

        setIsRegistering(true);
        setLoading(true); // Mulai loading untuk proses keseluruhan

        try {
            // 1. DAFTARKAN USER BARU
            const userRegistrationResponse = await registerUser(name, selectedRoleId, selectedLevelId);
            const userId = userRegistrationResponse.user_id;

            // Cari string nama Role dan Level yang sesuai dengan ID untuk API startInterview
            // Gunakan `?.` untuk optional chaining agar aman dari error
            const roleName = roles.find(r => r.id === selectedRoleId)?.role_name;
            const levelName = levels.find(l => l.id === selectedLevelId)?.level_name;

            if (!roleName || !levelName) {
                throw new Error("Pilihan Role atau Level tidak valid.");
            }

            // 2. MULAI SESI WAWANCARA
            // Kirim user ID yang baru dibuat, nama role, dan nama level
            handleStartSession(roleName, levelName, userId);

        } catch (err) {
            console.error("Gagal mendaftar atau memulai sesi:", err);
            // Tangkap response error dari backend jika ada
            const backendDetail = err.response?.data?.detail;
            setError(backendDetail || err.message || "Terjadi kesalahan saat memulai sesi.");
            setLoading(false); // 💡 KRITIS: Hentikan loading saat error terjadi di sini
        } finally {
            setIsRegistering(false);
            // Note: setLoading(false) untuk proses handleStartSession akan diurus di hook, 
            // tetapi kita pastikan loading utama dihentikan jika error terjadi sebelum hook.
        }
    };

    // 💡 PERBAIKAN: Logika disabled yang lebih ketat
    const isFormIncomplete = !name || !selectedRoleId || !selectedLevelId;
    const isProcessing = loading || isRegistering;

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-4">
            <div className="w-full max-w-lg p-8 space-y-6 bg-white rounded-xl shadow-2xl">
                <h1 className="text-3xl font-bold text-center text-blue-800">Mulai Wawancara AI</h1>
                {error && <p className="text-red-500 text-center">{error}</p>}

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Nama</label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="Masukkan Nama Anda"
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3 focus:ring-blue-500 focus:border-blue-500"
                            disabled={isProcessing}
                        />
                    </div>

                    <Dropdown
                        label="Pilih Posisi"
                        options={roles}
                        selectedId={selectedRoleId}
                        setSelectedId={setSelectedRoleId}
                        idKey="id"
                        nameKey="role_name"
                        disabled={isProcessing}
                    />
                    <Dropdown
                        label="Pilih Level"
                        options={levels}
                        selectedId={selectedLevelId}
                        setSelectedId={setSelectedLevelId}
                        idKey="id"
                        nameKey="level_name"
                        disabled={isProcessing}
                    />

                    {/* 💡 KRITIS: Disabled jika form belum lengkap ATAU sedang memproses */}
                    <Button type="submit" disabled={isProcessing || isFormIncomplete}>
                        {isProcessing ? 'Memproses...' : 'Mulai Wawancara'}
                    </Button>
                </form>
            </div>
        </div>
    );
};

export default HomePage;