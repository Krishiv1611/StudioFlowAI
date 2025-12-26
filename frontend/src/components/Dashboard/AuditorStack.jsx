import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, Tooltip as RechartsTooltip } from 'recharts';
import { Activity, ShieldCheck, Eye, TrendingUp } from 'lucide-react';

const AuditorStack = () => {
    // Mock Data for Charts
    const viralityData = [
        { name: 'Viral', value: 82 },
        { name: 'Dull', value: 18 },
    ];
    const reachData = [
        { platform: 'X', reach: 120 },      // X (Twitter)
        { platform: 'Insta', reach: 95 },   // Instagram
        { platform: 'LinkedIn', reach: 150 },// LinkedIn
    ];
    const COLORS = ['#d946ef', '#334155']; // Magenta to Slate

    return (
        <div className="h-full flex flex-col p-4 space-y-4 overflow-y-auto custom-scrollbar">
            <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-2">
                <Activity className="w-5 h-5 text-cyan-400" />
                Auditor Stack
            </h3>

            {/* Virality Probability */}
            <div className="p-4 bg-glass border border-glass-border rounded-xl">
                <div className="flex justify-between items-center mb-4">
                    <span className="text-sm text-gray-400">Virality Score</span>
                    <TrendingUp className="w-4 h-4 text-magenta-500 text-fuchsia-500" />
                </div>
                <div className="h-32 relative flex items-center justify-center">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={viralityData}
                                cx="50%"
                                cy="50%"
                                innerRadius={35}
                                outerRadius={50}
                                startAngle={180}
                                endAngle={0}
                                paddingAngle={5}
                                dataKey="value"
                                stroke="none"
                            >
                                {viralityData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                        </PieChart>
                    </ResponsiveContainer>
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-0 text-center">
                        <span className="text-2xl font-bold text-white">82%</span>
                    </div>
                </div>
                <div className="text-center text-xs text-fuchsia-400 mt-[-20px]">High Probability</div>
            </div>

            {/* Reach Projection */}
            <div className="p-4 bg-glass border border-glass-border rounded-xl">
                <div className="flex justify-between items-center mb-4">
                    <span className="text-sm text-gray-400">Reach Est. (K)</span>
                    <Eye className="w-4 h-4 text-cyan-400" />
                </div>
                <div className="h-32">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={reachData}>
                            <XAxis
                                dataKey="platform"
                                tick={{ fill: '#94a3b8', fontSize: 10 }}
                                axisLine={false}
                                tickLine={false}
                            />
                            <RechartsTooltip
                                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }}
                                itemStyle={{ color: '#e2e8f0' }}
                                cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                            />
                            <Bar dataKey="reach" fill="#06b6d4" radius={[4, 4, 0, 0]} barSize={20} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Sanity Check */}
            <div className="p-4 bg-glass border border-glass-border rounded-xl flex items-center justify-between">
                <div>
                    <div className="text-sm text-gray-400">Safety Check</div>
                    <div className="text-green-400 font-bold mt-1">Safe Content</div>
                </div>
                <ShieldCheck className="w-10 h-10 text-green-500 opacity-80" />
            </div>
        </div>
    );
};

export default AuditorStack;
