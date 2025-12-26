import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Lock, Key, Save } from 'lucide-react';
import { vaultService } from '../../services/vaultService';

const VaultModal = ({ isOpen, onClose }) => {
    const [keys, setKeys] = useState({
        openai_api_key: '',
        gemini_api_key: '',
        anthropic_api_key: '',
        serpapi_api_key: ''
    });

    useEffect(() => {
        if (isOpen) {
            loadKeys();
        }
    }, [isOpen]);

    const loadKeys = async () => {
        try {
            const data = await vaultService.getKeys();
            // Assuming data is { openai_api_key: "...", ... }
            if (data) setKeys(prev => ({ ...prev, ...data }));
        } catch (err) {
            console.error("Failed to load keys", err);
        }
    };

    const handleSave = async () => {
        try {
            await vaultService.updateKeys(keys);
            onClose();
            alert("Vault Secured.");
        } catch (err) {
            console.error("Failed to save keys", err);
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center">
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                    />

                    {/* Modal */}
                    <motion.div
                        initial={{ scale: 0.95, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.95, opacity: 0 }}
                        className="relative w-full max-w-lg p-6 bg-[#0f172a] border border-white/10 rounded-2xl shadow-2xl z-10"
                    >
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                <Lock className="w-5 h-5 text-purple-400" />
                                Secure Vault
                            </h2>
                            <button onClick={onClose} className="p-1 hover:bg-white/10 rounded text-gray-400 hover:text-white">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="space-y-6">
                            {/* Social Connect */}
                            <div>
                                <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">Connected Accounts</h3>
                                <div className="grid grid-cols-3 gap-3">
                                    {['Twitter', 'Instagram', 'LinkedIn'].map(platform => (
                                        <button key={platform} className="flex items-center justify-center gap-2 p-3 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 transition-colors">
                                            <span className={`w-2 h-2 rounded-full ${platform === 'Twitter' ? 'bg-blue-400' : platform === 'Instagram' ? 'bg-pink-500' : 'bg-blue-600'}`} />
                                            <span className="text-xs font-medium text-gray-300">{platform === 'Twitter' ? 'X' : platform}</span>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="border-t border-white/10 pt-4 space-y-4">
                                <h3 className="text-sm font-semibold text-gray-400 mb-2 uppercase tracking-wider">API Keys</h3>
                                {Object.keys(keys).map((key) => (
                                    <div key={key}>
                                        <label className="block text-xs uppercase tracking-wider text-gray-500 mb-1">
                                            {key.replace(/_/g, ' ')}
                                        </label>
                                        <div className="relative">
                                            <Key className="absolute left-3 top-3 w-4 h-4 text-gray-500" />
                                            <input
                                                type="password"
                                                value={keys[key]}
                                                onChange={(e) => setKeys({ ...keys, [key]: e.target.value })}
                                                className="w-full bg-black/40 border border-white/10 rounded-lg py-2.5 pl-10 pr-4 text-white text-sm focus:border-purple-500 outline-none transition-colors"
                                                placeholder="sk-..."
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="mt-8 flex justify-end">
                            <button
                                onClick={handleSave}
                                className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-medium transition-colors"
                            >
                                <Save className="w-4 h-4" />
                                Save Credentials
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};

export default VaultModal;
