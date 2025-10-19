// src/pages/HomePage.jsx

import React, { useState, useEffect } from 'react';
import { useInterviewSession } from '../hooks/useInterviewSession'; 
import { registerUser, fetchRoles, fetchLevels } from '../services/api';
import Dropdown from '../components/common/Dropdown';
import Button from '../components/common/Button';

const HomePage = () => {
    const [name, setName] = useState('');
    const [roles, setRoles] = useState([]);
    const [levels, setLevels] = useState([]);
    const [selectedRoleId, setSelectedRoleId] = useState(null); 
    const [selectedLevelId, setSelectedLevelId] = useState(null);

    const [isRegistering, setIsRegistering] = useState(false);
    const { loading, setLoading, error, setError, handleStartSession } = useInterviewSession(); 


    // 🟢 EFFECT: Mengambil data Role dan Level saat komponen dimuat
    useEffect(() => {
        const loadData = async () => {
            try {
                const [rolesData, levelsData] = await Promise.all([fetchRoles(), fetchLevels()]);
                setRoles(rolesData);
                setLevels(levelsData);

                // Set nilai default ke ID pertama jika ada
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
            alert("Mohon isi Nama, Role, dan Level dengan lengkap.");
            return;
        }

        setIsRegistering(true);
        setLoading(true);

        try {
            // 1. DAFTARKAN USER BARU
            const userRegistrationResponse = await registerUser(name, selectedRoleId, selectedLevelId);
            const userId = userRegistrationResponse.user_id;

            // Cari string nama Role dan Level yang sesuai dengan ID untuk API startInterview
            const roleName = roles.find(r => r.id === selectedRoleId)?.role_name;
            const levelName = levels.find(l => l.id === selectedLevelId)?.level_name;

            if (!roleName || !levelName) {
                throw new Error("Pilihan Role atau Level tidak valid.");
            }

            // 2. MULAI SESI WAWANCARA
            // 💡 PERBAIKAN KRITIS: Kirim selectedRoleId dan selectedLevelId ke hook
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

                    <Button type="submit" disabled={isProcessing || isFormIncomplete}>
                        {isProcessing ? 'Memproses...' : 'Mulai Wawancara'}
                    </Button>
                </form>
            </div>
        </div>
    );
};

export default HomePage;