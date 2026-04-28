import React, { useState, useEffect } from 'react';
// Nguon duy nhat cho version string — doc tu package.json qua vite.config.ts define
const APP_VERSION: string = import.meta.env.VITE_APP_VERSION ?? '0.0.0';
import { motion, AnimatePresence } from 'motion/react';
import { Play, X, Copy, Check, Loader2, AlertCircle } from 'lucide-react';

interface Props {
  open: boolean;
  onClose: () => void;
  onActivate?: (key: string) => Promise<{ ok: boolean; expires?: string; error?: string }>;
  machineId?: string;
}

const formatKey = (raw: string) => {
  const stripped = raw.replace(/[^A-Za-z0-9]/g, '').toUpperCase();
  const tooLong = stripped.length > 16;
  const clean = stripped.slice(0, 16);
  return { formatted: clean.match(/.{1,4}/g)?.join('-') ?? '', tooLong };
};

export default function LicenseModal({ open, onClose, onActivate, machineId = 'B4F2-9A1C-7E3D-2F8B' }: Props) {
  const [key, setKey] = useState('');
  const [keyTooLong, setKeyTooLong] = useState(false);
  const [state, setState] = useState<'idle' | 'validating' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!open) {
      setKey('');
      setKeyTooLong(false);
      setState('idle');
      setMessage(null);
    }
  }, [open]);

  const isValidFormat = key.replace(/-/g, '').length === 16;

  const handleActivate = async () => {
    if (!isValidFormat) return;
    setState('validating');
    setMessage(null);
    if (onActivate) {
      const r = await onActivate(key);
      if (r.ok) {
        setState('success');
        setMessage(`License valid — expires ${r.expires ?? 'Apr 27, 2027'}`);
      } else {
        setState('error');
        setMessage(r.error ?? 'Invalid license key.');
      }
    } else {
      setTimeout(() => {
        setState('success');
        setMessage('License valid — expires Apr 27, 2027');
      }, 900);
    }
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(machineId);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
          onClick={onClose}
        >
          <motion.div
            className="relative w-[560px] rounded-2xl bg-[#111116] border border-[#1F1F28] shadow-[0_24px_48px_rgba(0,0,0,0.6)] overflow-hidden"
            initial={{ scale: 0.96, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.96, opacity: 0 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={onClose}
              className="absolute top-4 right-4 w-9 h-9 rounded-lg flex items-center justify-center text-[#A1A1AA] hover:text-white hover:bg-[#1F1F28] transition-colors"
              aria-label="Close"
            >
              <X size={18} />
            </button>

            <div className="px-8 pt-8 pb-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#FF6B35] to-[#FF8159] flex items-center justify-center">
                  <Play size={14} className="text-white fill-white ml-0.5" />
                </div>
                <div>
                  <div className="text-[20px] font-semibold leading-tight text-[#FAFAFA]">VEO Pipeline Pro</div>
                  <div className="text-[12px] text-[#71717A] leading-tight mt-0.5">Commercial Edition v{APP_VERSION}</div>
                </div>
              </div>

              <h2 className="text-[24px] font-semibold text-[#FAFAFA] tracking-tight">Activate License</h2>
              <p className="text-[14px] text-[#A1A1AA] mt-1">Enter your license key to unlock all features.</p>

              <div className="mt-6">
                <input
                  value={key}
                  onChange={(e) => {
                    const r = formatKey(e.target.value);
                    setKey(r.formatted);
                    setKeyTooLong(r.tooLong);
                  }}
                  placeholder="XXXX-XXXX-XXXX-XXXX"
                  className="w-full h-14 px-4 rounded-lg bg-[#16161D] border border-[#1F1F28] focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/40 outline-none font-mono text-[16px] tracking-wider text-[#FAFAFA] placeholder:text-[#52525B] transition-colors"
                  spellCheck={false}
                  autoFocus
                />
              </div>

              {keyTooLong && (
                <p className="mt-1.5 text-[12px] text-[#EF4444]">
                  Key vuot 16 ky tu, da cat — kiem tra lai
                </p>
              )}

              <div className="mt-3 flex items-center justify-between bg-[#0E0E13] border border-[#1F1F28] rounded-lg px-4 py-3">
                <div>
                  <div className="text-[12px] text-[#71717A]">This Machine</div>
                  <div className="font-mono text-[13px] text-[#FAFAFA] mt-0.5">{machineId}</div>
                </div>
                <button
                  onClick={handleCopy}
                  className="w-8 h-8 rounded-md flex items-center justify-center text-[#A1A1AA] hover:text-white hover:bg-[#1F1F28] transition-colors"
                  aria-label="Copy machine ID"
                >
                  {copied ? <Check size={16} className="text-[#22C55E]" /> : <Copy size={15} />}
                </button>
              </div>

              {state !== 'idle' && (
                <div className={`mt-4 flex items-center gap-2 text-[13px] ${
                  state === 'validating' ? 'text-[#A1A1AA]' :
                  state === 'success' ? 'text-[#22C55E]' :
                  'text-[#EF4444]'
                }`}>
                  {state === 'validating' && <Loader2 size={14} className="animate-spin" />}
                  {state === 'success' && <Check size={14} />}
                  {state === 'error' && <AlertCircle size={14} />}
                  <span>{state === 'validating' ? 'Verifying license...' : message}</span>
                </div>
              )}
            </div>

            <div className="border-t border-[#1F1F28] px-8 py-4 flex items-center justify-between">
              <a
                href="https://zalo.me/0345431884"
                target="_blank"
                rel="noreferrer"
                className="text-[14px] text-[#FF6B35] hover:text-[#FF8159] font-medium transition-colors"
              >
                Buy License
              </a>
              <button
                onClick={handleActivate}
                disabled={!isValidFormat || state === 'validating'}
                className="h-10 px-6 rounded-lg bg-[#FF6B35] hover:bg-[#FF8159] disabled:bg-[#1F1F28] disabled:text-[#52525B] disabled:cursor-not-allowed text-white text-[14px] font-semibold transition-colors flex items-center gap-2 min-w-[120px] justify-center"
              >
                {state === 'validating' ? <Loader2 size={16} className="animate-spin" /> : 'Activate'}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
