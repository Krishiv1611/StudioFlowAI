import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { AreaChart, Area, ResponsiveContainer, Tooltip } from 'recharts';
import { Radio, Activity, Zap } from 'lucide-react';

// Mock data for trends (replace with backend data later)
const MOCK_TRENDS = [
    { id: 1, topic: "r/Technology", buzz: 4.2, data: [{ v: 10 }, { v: 20 }, { v: 15 }, { v: 40 }, { v: 35 }, { v: 60 }] },
    { id: 2, topic: "#AIRevolution", buzz: 3.8, data: [{ v: 20 }, { v: 10 }, { v: 25 }, { v: 15 }, { v: 30 }, { v: 45 }] },
    { id: 3, topic: "Semantic Web", buzz: 3.5, data: [{ v: 5 }, { v: 15 }, { v: 10 }, { v: 25 }, { v: 20 }, { v: 30 }] },
];

const ScoutRadar = () => {
    const [trends, setTrends] = useState(MOCK_TRENDS);

    return (
        <div className="h-full flex flex-col p-4 space-y-4 overflow-y-auto custom-scrollbar">
            <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Radio className="w-5 h-5 text-green-400 animate-pulse" />
                    Scout Radar
                </h3>
                <span className="text-xs text-gray-400 bg-white/5 px-2 py-1 rounded-full border border-white/10">
                    Live Feed
                </span>
            </div>

            {trends.map((trend, index) => (
                <motion.div
                    key={trend.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="group relative p-4 bg-glass border border-glass-border rounded-xl hover:bg-white/5 transition-all cursor-pointer overflow-hidden"
                >
                    {/* Hover Glow */}
                    <div className="absolute inset-0 bg-green-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                    <div className="flex justify-between items-start mb-2 relative z-10">
                        <div>
                            <h4 className="font-semibold text-gray-100">{trend.topic}</h4>
                            <div className="flex items-center gap-1 text-xs text-green-400 mt-1">
                                <Zap className="w-3 h-3" />
                                <span>Buzz Score: {trend.buzz}</span>
                            </div>
                        </div>
                        <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_10px_#22c55e] animate-pulse" />
                    </div>

                    {/* Sparkline Chart */}
                    <div className="h-16 w-full relative z-10 opacity-70 group-hover:opacity-100 transition-opacity">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={trend.data}>
                                <defs>
                                    <linearGradient id={`gradient-${trend.id}`} x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <Area
                                    type="monotone"
                                    dataKey="v"
                                    stroke="#22c55e"
                                    fillOpacity={1}
                                    fill={`url(#gradient-${trend.id})`}
                                    strokeWidth={2}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>
            ))}
        </div>
    );
};

export default ScoutRadar;
