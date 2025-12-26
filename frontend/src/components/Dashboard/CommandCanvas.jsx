import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, Sparkles, Send, Save, CheckCircle } from 'lucide-react';
import { agentService } from '../../services/agentService';
import { postService } from '../../services/postService';

const CommandCanvas = () => {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([]); // Chat history
    const [isProcessing, setIsProcessing] = useState(false);
    const [activeAgent, setActiveAgent] = useState('Idle'); // 'Scripter', 'Engineer', 'Sentry'
    const [selectedPlatform, setSelectedPlatform] = useState('Twitter'); // Default to X (Twitter backend enum)

    // Auto-scroll to bottom of chat
    const messagesEndRef = useRef(null);
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };
    useEffect(scrollToBottom, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsProcessing(true);
        setActiveAgent('Scripter'); // Simulate getting busy

        try {
            // Simulate agent handoff sequence for visual effect
            setTimeout(() => setActiveAgent('Engineer'), 1500);
            setTimeout(() => setActiveAgent('Sentry'), 3000);

            // Call backend agent (Guru mode for now for chat)
            const result = await agentService.chatWithGuru(userMsg.content, messages);

            setMessages(prev => [...prev, { role: 'assistant', content: result.response }]);
            setActiveAgent('Idle');
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, { role: 'system', content: "Error communicating with the grid." }]);
            setActiveAgent('Idle');
        } finally {
            setIsProcessing(false);
        }
    };

    const handleSaveDraft = async () => {
        // Save last AI response as draft
        const lastMsg = messages.filter(m => m.role === 'assistant').pop();
        if (lastMsg) {
            try {
                await postService.createPost({
                    content: lastMsg.content,
                    platform: selectedPlatform,
                    scheduled_for: null
                });
                alert(`Draft Saved for ${selectedPlatform === 'Twitter' ? 'X' : selectedPlatform}!`);
            } catch (err) {
                console.error("Failed to save draft", err);
            }
        }
    };

    return (
        <div className="h-full flex flex-col relative bg-glass/30 backdrop-blur-sm rounded-2xl border border-glass-border overflow-hidden">

            {/* Agent Status Bar (Handoff Animation) */}
            <div className="h-14 border-b border-white/10 flex items-center justify-between px-6 bg-black/20">
                <div className="flex items-center gap-3">
                    <Bot className={`w-5 h-5 ${isProcessing ? 'text-purple-400 animate-bounce' : 'text-gray-400'}`} />
                    <AnimatePresence mode="wait">
                        <motion.span
                            key={activeAgent}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="font-mono text-sm text-purple-300"
                        >
                            {activeAgent === 'Idle' ? 'System Ready' : `${activeAgent} Active...`}
                        </motion.span>
                    </AnimatePresence>
                </div>
                {/* Actions */}
                <div className="flex gap-4 items-center">
                    {/* Platform Selector */}
                    <div className="flex bg-black/30 rounded-lg p-1 border border-white/5">
                        {['Twitter', 'Instagram', 'LinkedIn'].map((p) => (
                            <button
                                key={p}
                                onClick={() => setSelectedPlatform(p)}
                                className={`px-3 py-1 text-xs rounded-md transition-all ${selectedPlatform === p
                                        ? 'bg-purple-600 text-white shadow-lg'
                                        : 'text-gray-500 hover:text-gray-300'
                                    }`}
                            >
                                {p === 'Twitter' ? 'X' : p}
                            </button>
                        ))}
                    </div>

                    <button
                        onClick={handleSaveDraft}
                        className="p-2 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white transition-colors"
                        title="Save as Draft"
                    >
                        <Save className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Chat/Editor Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
                {messages.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-gray-500 opacity-50">
                        <Bot className="w-16 h-16 mb-4" />
                        <p>Initialize a task for the Agent Swarm</p>
                    </div>
                )}

                {messages.map((msg, idx) => (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div className={`max-w-[80%] p-4 rounded-2xl border ${msg.role === 'user'
                            ? 'bg-purple-600/20 border-purple-500/30 text-purple-100'
                            : 'bg-white/5 border-white/10 text-gray-100'
                            }`}>
                            <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                        </div>
                    </motion.div>
                ))}

                {isProcessing && (
                    <div className="flex justify-start">
                        <div className="flex space-x-2 p-4 bg-white/5 rounded-2xl border border-white/10">
                            <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                            <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                            <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-black/40 border-t border-white/10">
                <div className="relative flex items-center">
                    <Sparkles className="absolute left-4 w-5 h-5 text-purple-400" />
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Instruct the swarm..."
                        className="w-full bg-white/5 border border-white/10 rounded-xl py-4 pl-12 pr-14 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all"
                        disabled={isProcessing}
                    />
                    <button
                        onClick={handleSend}
                        disabled={!input.trim() || isProcessing}
                        className="absolute right-2 p-2 bg-purple-600 hover:bg-purple-500 rounded-lg text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Send className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CommandCanvas;
