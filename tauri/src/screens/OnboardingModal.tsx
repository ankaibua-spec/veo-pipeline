import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  X, ChevronLeft, ChevronRight, Check, Sparkles, Eye, EyeOff,
  Upload, FolderOpen, CheckCircle2,
} from 'lucide-react';

interface Props {
  open: boolean;
  onClose: () => void;
  onFinish?: () => void;
}

const STEPS = ['Welcome', 'API Keys', 'Drive Sync', 'Done'];

export default function OnboardingModal({ open, onClose, onFinish }: Props) {
  const [step, setStep] = useState(0);
  const [direction, setDirection] = useState<1 | -1>(1);

  const [keys, setKeys] = useState({
    gemini: '',
    openai: '',
    twelvedata: '',
    telegram: '',
  });
  const [show, setShow] = useState({
    gemini: false, openai: false, twelvedata: false, telegram: false,
  });
  const [driveFolder, setDriveFolder] = useState('');

  const next = () => {
    if (step < STEPS.length - 1) {
      setDirection(1);
      setStep(step + 1);
    } else {
      onFinish?.();
      onClose();
    }
  };
  const back = () => {
    if (step > 0) {
      setDirection(-1);
      setStep(step - 1);
    }
  };

  const ApiInput = ({
    field, label, optional, getUrl,
  }: { field: keyof typeof keys; label: string; optional?: boolean; getUrl: string }) => (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className="text-[14px] text-[#FAFAFA] font-medium">
          {label} {optional && <span className="text-[#71717A] font-normal">(optional)</span>}
        </label>
        <a href={getUrl} target="_blank" rel="noreferrer" className="text-[12px] text-[#FF6B35] hover:text-[#FF8159]">Get key</a>
      </div>
      <div className="relative">
        <input
          type={show[field] ? 'text' : 'password'}
          value={keys[field]}
          onChange={(e) => setKeys({ ...keys, [field]: e.target.value })}
          placeholder={`Paste ${label.toLowerCase()}...`}
          className="w-full h-11 pl-4 pr-10 rounded-lg bg-[#16161D] border border-[#1F1F28] focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/40 outline-none text-[14px] text-[#FAFAFA] placeholder:text-[#52525B] font-mono"
        />
        <button
          onClick={() => setShow({ ...show, [field]: !show[field] })}
          className="absolute right-2 top-1/2 -translate-y-1/2 w-7 h-7 rounded flex items-center justify-center text-[#71717A] hover:text-white hover:bg-[#1F1F28]"
        >
          {show[field] ? <EyeOff size={14} /> : <Eye size={14} />}
        </button>
      </div>
    </div>
  );

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
        >
          <motion.div
            className="relative w-[880px] h-[600px] rounded-2xl bg-[#111116] border border-[#1F1F28] shadow-[0_24px_48px_rgba(0,0,0,0.6)] flex flex-col overflow-hidden"
            initial={{ scale: 0.96, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.96, opacity: 0 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
          >
            {/* Top bar */}
            <div className="h-16 px-8 border-b border-[#1F1F28] flex items-center justify-between shrink-0">
              <div>
                <div className="text-[18px] font-semibold text-[#FAFAFA]">Setup Wizard</div>
                <div className="text-[13px] text-[#71717A]">Step {step + 1} of {STEPS.length}</div>
              </div>
              <button
                onClick={onClose}
                className="w-9 h-9 rounded-lg flex items-center justify-center text-[#A1A1AA] hover:text-white hover:bg-[#1F1F28]"
              >
                <X size={18} />
              </button>
            </div>

            {/* Stepper */}
            <div className="h-14 px-8 border-b border-[#1F1F28] flex items-center shrink-0">
              <div className="flex items-center w-full">
                {STEPS.map((s, i) => (
                  <React.Fragment key={s}>
                    <div className="flex flex-col items-center gap-1">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-[12px] font-semibold transition-all ${
                        i < step ? 'bg-[#FF6B35] text-white' :
                        i === step ? 'bg-[#FF6B35] text-white ring-4 ring-[#FF6B35]/20' :
                        'bg-[#16161D] border border-[#1F1F28] text-[#71717A]'
                      }`}>
                        {i < step ? <Check size={14} /> : i + 1}
                      </div>
                      <span className={`text-[12px] ${i === step ? 'text-[#FAFAFA]' : 'text-[#A1A1AA]'}`}>{s}</span>
                    </div>
                    {i < STEPS.length - 1 && (
                      <div className={`flex-1 h-px mx-2 ${i < step ? 'bg-[#FF6B35]' : 'bg-[#1F1F28]'}`} />
                    )}
                  </React.Fragment>
                ))}
              </div>
            </div>

            {/* Body */}
            <div className="flex-1 overflow-hidden relative">
              <AnimatePresence mode="wait" custom={direction}>
                <motion.div
                  key={step}
                  custom={direction}
                  initial={{ x: direction * 60, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  exit={{ x: direction * -60, opacity: 0 }}
                  transition={{ duration: 0.25, ease: 'easeOut' }}
                  className="absolute inset-0 p-10 overflow-y-auto"
                >
                  {step === 0 && (
                    <div className="max-w-[600px] mx-auto text-center">
                      <div className="w-24 h-24 mx-auto rounded-full bg-gradient-to-br from-[#FF6B35] to-[#FF8159] flex items-center justify-center mb-6">
                        <Sparkles size={40} className="text-white" />
                      </div>
                      <h2 className="text-[28px] font-semibold text-[#FAFAFA] tracking-tight">Welcome to VEO Pipeline Pro</h2>
                      <p className="text-[15px] text-[#A1A1AA] mt-3">Let's set up your workspace in 3 quick steps.</p>
                      <ul className="mt-8 space-y-3 text-left max-w-[480px] mx-auto">
                        {[
                          'Generate Veo3 videos in batch',
                          'Auto-sync to Google Drive',
                          'Manage 100+ Flow accounts',
                        ].map((t) => (
                          <li key={t} className="flex items-center gap-3 text-[14px] text-[#FAFAFA]">
                            <CheckCircle2 size={18} className="text-[#22C55E] shrink-0" />
                            {t}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {step === 1 && (
                    <div className="max-w-[600px] mx-auto">
                      <h3 className="text-[20px] font-semibold text-[#FAFAFA]">Connect Your Services</h3>
                      <p className="text-[13px] text-[#A1A1AA] mt-1 mb-6">Paste your API keys. You can update them later in Settings.</p>
                      <div className="space-y-4">
                        <ApiInput field="gemini" label="Gemini API Key" getUrl="https://aistudio.google.com/apikey" />
                        <ApiInput field="openai" label="OpenAI API Key" optional getUrl="https://platform.openai.com/api-keys" />
                        <ApiInput field="twelvedata" label="TwelveData" optional getUrl="https://twelvedata.com/account/api-keys" />
                        <ApiInput field="telegram" label="Telegram Bot Token" optional getUrl="https://t.me/BotFather" />
                      </div>
                    </div>
                  )}

                  {step === 2 && (
                    <div className="max-w-[600px] mx-auto">
                      <h3 className="text-[20px] font-semibold text-[#FAFAFA]">Google Drive Integration</h3>
                      <p className="text-[13px] text-[#A1A1AA] mt-1 mb-6">Pick one method. OAuth recommended.</p>

                      <div className="space-y-3 mb-6">
                        <div className="border border-[#1F1F28] rounded-xl p-5 bg-[#16161D]">
                          <div className="text-[12px] uppercase tracking-wide text-[#71717A] mb-2">Recommended</div>
                          <button className="w-full h-11 bg-white text-[#0B0B0F] rounded-lg font-medium text-[14px] hover:bg-zinc-100 transition-colors flex items-center justify-center gap-2">
                            <span className="font-bold text-[#4285F4]">G</span> Sign in with Google
                          </button>
                        </div>

                        <div className="border border-dashed border-[#1F1F28] rounded-xl p-5 bg-[#0E0E13] hover:border-[#FF6B35]/40 transition-colors cursor-pointer">
                          <div className="flex flex-col items-center justify-center h-32 text-[#71717A]">
                            <Upload size={28} className="mb-2" />
                            <div className="text-[14px] text-[#FAFAFA]">Drop credentials.json or click to browse</div>
                            <div className="text-[12px] mt-1">Service Account method</div>
                          </div>
                        </div>
                      </div>

                      <label className="text-[14px] text-[#FAFAFA] font-medium block mb-2">Default Drive Folder ID</label>
                      <div className="flex gap-2">
                        <input
                          value={driveFolder}
                          onChange={(e) => setDriveFolder(e.target.value)}
                          placeholder="13sUXPBdGV-HzBwUdcUGSadl_kC9YUFyJ"
                          className="flex-1 h-11 px-4 rounded-lg bg-[#16161D] border border-[#1F1F28] focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/40 outline-none text-[14px] text-[#FAFAFA] placeholder:text-[#52525B] font-mono"
                        />
                        <button className="h-11 px-4 rounded-lg border border-[#1F1F28] text-[#FAFAFA] hover:bg-[#1F1F28] transition-colors flex items-center gap-2 text-[14px]">
                          <FolderOpen size={16} /> Browse
                        </button>
                      </div>
                    </div>
                  )}

                  {step === 3 && (
                    <div className="max-w-[480px] mx-auto text-center pt-8">
                      <div className="w-24 h-24 mx-auto rounded-full bg-[#22C55E]/15 border border-[#22C55E]/30 flex items-center justify-center mb-6">
                        <Check size={42} className="text-[#22C55E]" />
                      </div>
                      <h2 className="text-[28px] font-semibold text-[#FAFAFA] tracking-tight">All Set!</h2>
                      <p className="text-[15px] text-[#A1A1AA] mt-3">Your workspace is ready. Start generating videos now.</p>
                      <button
                        onClick={next}
                        className="mt-8 h-11 px-8 rounded-lg bg-[#FF6B35] hover:bg-[#FF8159] text-white font-semibold transition-colors"
                      >
                        Open Dashboard
                      </button>
                    </div>
                  )}
                </motion.div>
              </AnimatePresence>
            </div>

            {/* Footer */}
            {step < STEPS.length - 1 && (
              <div className="h-16 px-8 border-t border-[#1F1F28] flex items-center justify-between shrink-0">
                <button
                  onClick={back}
                  disabled={step === 0}
                  className="h-9 px-4 rounded-lg text-[#A1A1AA] hover:text-white hover:bg-[#1F1F28] disabled:opacity-30 disabled:cursor-not-allowed transition-colors flex items-center gap-1.5 text-[14px]"
                >
                  <ChevronLeft size={16} /> Back
                </button>
                <button
                  onClick={next}
                  className="h-10 px-6 rounded-lg bg-[#FF6B35] hover:bg-[#FF8159] text-white font-semibold transition-colors flex items-center gap-1.5 text-[14px]"
                >
                  Next <ChevronRight size={16} />
                </button>
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
