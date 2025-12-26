import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Calendar as CalendarIcon, Clock } from 'lucide-react';
import { calendarService } from '../../services/calendarService';

const CalendarOverlay = ({ isOpen, onClose }) => {
    const [events, setEvents] = useState([]);

    useEffect(() => {
        if (isOpen) {
            loadSchedule();
        }
    }, [isOpen]);

    const loadSchedule = async () => {
        try {
            const data = await calendarService.getSchedule();
            setEvents(data || []);
        } catch (err) {
            console.error("Failed to load schedule", err);
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Side Drawer Animation */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
                    />

                    <motion.div
                        initial={{ x: '100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '100%' }}
                        transition={{ type: "spring", stiffness: 300, damping: 30 }}
                        className="fixed right-0 top-0 h-full w-full max-w-md bg-[#0d0d0d] border-l border-white/10 p-6 z-50 shadow-2xl overflow-y-auto"
                    >
                        <div className="flex justify-between items-center mb-8">
                            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                <CalendarIcon className="w-5 h-5 text-cyan-400" />
                                Content Schedule
                            </h2>
                            <button onClick={onClose} className="p-1 hover:bg-white/10 rounded text-gray-400 hover:text-white">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="space-y-4">
                            {events.length === 0 ? (
                                <div className="text-center py-10 text-gray-500">
                                    <p>No upcoming posts scheduled.</p>
                                </div>
                            ) : (
                                events.map((event, idx) => (
                                    <div key={idx} className="p-4 bg-glass border border-glass-border rounded-xl">
                                        <div className="flex justify-between items-start">
                                            <span className={`text-xs px-2 py-1 rounded border ${event.platform === 'Twitter' ? 'bg-blue-500/10 border-blue-500/30 text-blue-400' :
                                                    event.platform === 'Instagram' ? 'bg-pink-500/10 border-pink-500/30 text-pink-400' :
                                                        'bg-blue-700/10 border-blue-700/30 text-blue-300'
                                                }`}>
                                                {event.platform === 'Twitter' ? 'X' : event.platform}
                                            </span>
                                            <span className="text-xs text-gray-400 flex items-center gap-1">
                                                <Clock className="w-3 h-3" />
                                                {new Date(event.scheduled_for).toLocaleDateString()}
                                            </span>
                                        </div>
                                        <p className="mt-2 text-sm text-gray-200 line-clamp-2">
                                            {event.content}
                                        </p>
                                    </div>
                                ))
                            )}
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};

export default CalendarOverlay;
