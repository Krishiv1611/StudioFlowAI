import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LogOut, Calendar, Settings, Grid, Lock } from 'lucide-react';
import { authService } from '../../services/authService';

import ScoutRadar from './ScoutRadar';
import CommandCanvas from './CommandCanvas';
import AuditorStack from './AuditorStack';
import VaultModal from '../Overlay/VaultModal';
import CalendarOverlay from '../Overlay/CalendarOverlay';

const CommandCenter = () => {
    const navigate = useNavigate();
    const [showVault, setShowVault] = useState(false);
    const [showCalendar, setShowCalendar] = useState(false);

    const handleLogout = () => {
        authService.logout();
    };

    return (
        <div className="flex h-screen w-full bg-[#0d0d0d] text-white overflow-hidden">
            {/* Overlays */}
            <VaultModal isOpen={showVault} onClose={() => setShowVault(false)} />
            <CalendarOverlay isOpen={showCalendar} onClose={() => setShowCalendar(false)} />

            {/* Nav Dock (Slim Sidebar) */}
            <motion.div
                initial={{ x: -50 }} animate={{ x: 0 }}
                className="w-16 border-r border-white/10 flex flex-col items-center py-6 bg-glass backdrop-blur-md z-20"
            >
                <div className="mb-8">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center font-bold text-sm">
                        SF
                    </div>
                </div>

                <nav className="flex-1 flex flex-col gap-6 w-full items-center">
                    <ButtonItem icon={<Grid size={20} />} active label="Dashboard" />
                    <ButtonItem icon={<Calendar size={20} />} label="Schedule" onClick={() => setShowCalendar(true)} />
                    <ButtonItem icon={<Lock size={20} />} label="Vault" onClick={() => setShowVault(true)} />
                    <ButtonItem icon={<Settings size={20} />} label="Settings" />
                </nav>

                <div className="mt-auto">
                    <button
                        onClick={handleLogout}
                        className="p-3 text-gray-500 hover:text-red-400 transition-colors rounded-xl hover:bg-white/5"
                        title="Logout"
                    >
                        <LogOut size={20} />
                    </button>
                </div>
            </motion.div>

            {/* Main Grid Layout */}
            <main className="flex-1 grid grid-cols-12 gap-0 h-full relative">
                {/* Ambient Background Glows */}
                <div className="absolute top-0 left-0 w-full h-[500px] bg-purple-900/10 blur-[120px] pointer-events-none" />

                {/* Left Panel: Scout (20%) */}
                <div className="col-span-3 border-r border-white/5 bg-black/20 backdrop-blur-sm z-10 relative">
                    <ScoutRadar />
                </div>

                {/* Center Panel: Command (50%) */}
                <div className="col-span-6 p-6 z-10 relative flex flex-col">
                    <CommandCanvas />
                </div>

                {/* Right Panel: Auditor (30%) */}
                <div className="col-span-3 border-l border-white/5 bg-black/20 backdrop-blur-sm z-10 relative">
                    <AuditorStack />
                </div>
            </main>
        </div>
    );
};

const ButtonItem = ({ icon, active, onClick, label }) => (
    <button
        onClick={onClick}
        className={`p-3 rounded-xl transition-all duration-300 group relative ${active
                ? 'bg-white/10 text-white shadow-[0_0_15px_rgba(255,255,255,0.1)]'
                : 'text-gray-500 hover:text-white hover:bg-white/5'
            }`}
    >
        {icon}
        {/* Tooltip */}
        <span className="absolute left-14 bg-gray-900 text-xs px-2 py-1 rounded border border-white/10 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
            {label}
        </span>
    </button>
);

export default CommandCenter;
