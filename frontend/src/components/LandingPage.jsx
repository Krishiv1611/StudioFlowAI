import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Bot, Zap, Shield, ArrowRight, BarChart3 } from 'lucide-react';

const LandingPage = () => {
    return (
        <div className="min-h-screen bg-[#0d0d0d] text-white overflow-x-hidden relative selection:bg-purple-500/30">
            {/* Background Effects */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
                <div className="absolute top-[-20%] left-[20%] w-[500px] h-[500px] bg-purple-600/20 rounded-full blur-[120px]" />
                <div className="absolute bottom-[-10%] right-[10%] w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[150px]" />
                <div className="absolute top-[40%] left-[-10%] w-[400px] h-[400px] bg-cyan-500/10 rounded-full blur-[100px]" />
            </div>

            {/* Navbar */}
            <nav className="relative z-20 flex items-center justify-between px-8 py-6 border-b border-white/5 bg-black/20 backdrop-blur-md">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
                        <Bot className="w-5 h-5 text-white" />
                    </div>
                    <span className="font-bold text-xl tracking-tight">StudioFlow AI</span>
                </div>
                <div className="flex items-center gap-4">
                    <Link to="/login" className="px-4 py-2 text-sm text-gray-300 hover:text-white transition-colors">
                        Log In
                    </Link>
                    <Link to="/signup" className="px-5 py-2 text-sm font-medium bg-white text-black rounded-lg hover:bg-gray-100 transition-colors shadow-[0_0_15px_rgba(255,255,255,0.2)]">
                        Initialize Agent
                    </Link>
                </div>
            </nav>

            {/* Hero Section */}
            <main className="relative z-10 container mx-auto px-6 pt-20 pb-32">
                <div className="max-w-4xl mx-auto text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                    >
                        <span className="inline-block px-3 py-1 mb-6 text-xs font-semibold tracking-wider text-purple-400 uppercase bg-purple-500/10 rounded-full border border-purple-500/20">
                            The Future of Content Operations
                        </span>
                        <h1 className="text-6xl md:text-7xl font-bold tracking-tighter mb-8 bg-gradient-to-b from-white to-gray-400 bg-clip-text text-transparent">
                            Command the Swarm. <br /> Dominate the Algorithm.
                        </h1>
                        <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
                            Orchestrate a team of specialized AI agents to scout trends, draft viral content, and optimize your reach across X, Instagram, and LinkedIn.
                        </p>

                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                            <Link to="/signup" className="group relative px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl font-semibold text-lg overflow-hidden transition-all hover:scale-105 shadow-[0_0_30px_rgba(124,58,237,0.3)]">
                                <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
                                <span className="relative flex items-center gap-2">
                                    Start Command Center <ArrowRight className="w-5 h-5" />
                                </span>
                            </Link>
                            <Link to="/login" className="px-8 py-4 bg-white/5 border border-white/10 rounded-xl font-semibold text-lg hover:bg-white/10 transition-all">
                                Live Demo
                            </Link>
                        </div>
                    </motion.div>
                </div>

                {/* Feature Grid */}
                <div className="mt-32 grid md:grid-cols-3 gap-8">
                    {[
                        { icon: <Zap className="w-6 h-6 text-yellow-400" />, title: "Scout Radar", desc: "Real-time trend analysis from Reddit & Semantic Web." },
                        { icon: <Bot className="w-6 h-6 text-purple-400" />, title: "Agent Swarm", desc: "Scripter, Engineer, and Sentry agents working in unison." },
                        { icon: <BarChart3 className="w-6 h-6 text-cyan-400" />, title: "Auditor Metrics", desc: "Predictive virality scores and reach projections." }
                    ].map((feature, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: i * 0.2 }}
                            className="p-8 rounded-2xl bg-glass border border-glass-border hover:bg-white/5 transition-colors group"
                        >
                            <div className="w-12 h-12 rounded-lg bg-white/5 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                {feature.icon}
                            </div>
                            <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                            <p className="text-gray-400 leading-relaxed">{feature.desc}</p>
                        </motion.div>
                    ))}
                </div>
            </main>
        </div>
    );
};

export default LandingPage;
