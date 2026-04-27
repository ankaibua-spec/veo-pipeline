import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  X, HardDrive, User, Folder, Settings2, Clock, Globe, Check,
  Plus, ChevronDown, Upload,
} from 'lucide-react';

interface Props {
  open: boolean;
  onClose: () => void;
  connected?: boolean;
  email?: string;
}

type Tab = 'account' | 'folders' | 'rules' | 'schedule';

const TABS: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: 'account', label: 'Account', icon: <User size={16} /> },
  { id: 'folders', label: 'Folders', icon: <Folder size={16} /> },
  { id: 'rules', label: 'Sync Rules', icon: <Settings2 size={16} /> },
  { id: 'schedule', label: 'Schedule', icon: <Clock size={16} /> },
];

const PIPELINES = [
  { name: 'English Shorts', folder: 'TikTok Affiliate / Shorts' },
  { name: 'Pronunciation', folder: 'TikTok Affiliate / Pronunciation' },
  { name: 'ASMR', folder: 'TikTok Affiliate / ASMR' },
];

const Toggle = ({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) => (
  <button
    onClick={() => onChange(!checked)}
    className={`relative w-10 h-6 rounded-full transition-colors ${checked ? 'bg-[#FF6B35]' : 'bg-[#1F1F28]'}`}
  >
    <span className={`absolute top-0.5 w-5 h-5 rounded-full bg-white transition-transform ${checked ? 'translate-x-[18px]' : 'translate-x-0.5'}`} />
  </button>
);

export default function DriveSyncModal({ open, onClose, connected = true, email = 'truonghoa.gtvt@gmail.com' }: Props) {
  const [tab, setTab] = useState<Tab>('account');
  const [rules, setRules] = useState({
    autoSync: true,
    deleteLocal: false,
    compress: false,
    notifyErrors: true,
  });
  const [schedule, setSchedule] = useState<'realtime' | 'minutes' | 'daily' | 'manual'>('realtime');
  const [interval, setInterval] = useState(30);
  const [dirty, setDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const markDirty = () => { setDirty(true); setSaved(false); };
  const handleSave = () => {
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      setDirty(false);
      setSaved(true);
    }, 800);
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
          onClick={onClose}
        >
          <motion.div
            className="relative w-[960px] h-[640px] rounded-2xl bg-[#111116] border border-[#1F1F28] shadow-[0_24px_48px_rgba(0,0,0,0.6)] flex flex-col overflow-hidden"
            initial={{ scale: 0.96, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.96, opacity: 0 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Top bar */}
            <div className="h-16 px-8 border-b border-[#1F1F28] flex items-center justify-between shrink-0">
              <div className="flex items-center gap-3">
                <HardDrive size={20} className="text-[#FF6B35]" />
                <div className="text-[18px] font-semibold text-[#FAFAFA]">Drive Sync Settings</div>
                <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium ml-3 ${
                  connected ? 'bg-[#22C55E]/15 text-[#22C55E]' : 'bg-[#1F1F28] text-[#A1A1AA]'
                }`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-[#22C55E]' : 'bg-[#71717A]'}`} />
                  {connected ? 'Connected' : 'Not connected'}
                </div>
              </div>
              <button onClick={onClose} className="w-9 h-9 rounded-lg flex items-center justify-center text-[#A1A1AA] hover:text-white hover:bg-[#1F1F28]">
                <X size={18} />
              </button>
            </div>

            {/* Body */}
            <div className="flex-1 flex overflow-hidden">
              {/* Left nav */}
              <div className="w-64 bg-[#0E0E13] border-r border-[#1F1F28] p-3 shrink-0">
                {TABS.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setTab(t.id)}
                    className={`w-full h-10 px-3 mb-1 rounded-lg flex items-center gap-3 text-[14px] transition-colors relative ${
                      tab === t.id
                        ? 'bg-[#1F1F28] text-[#FAFAFA]'
                        : 'text-[#A1A1AA] hover:bg-[#16161D] hover:text-[#FAFAFA]'
                    }`}
                  >
                    {tab === t.id && <span className="absolute left-0 top-2 bottom-2 w-[3px] rounded-r bg-[#FF6B35]" />}
                    {t.icon}
                    <span>{t.label}</span>
                  </button>
                ))}
              </div>

              {/* Right content */}
              <div className="flex-1 overflow-y-auto p-8">
                {tab === 'account' && (
                  <div>
                    <div className="text-[18px] font-semibold text-[#FAFAFA]">Connected Account</div>
                    <div className="text-[13px] text-[#A1A1AA] mt-1">Sign in with Google for the simplest setup.</div>

                    <div className="mt-5 border border-[#1F1F28] rounded-xl p-5 flex items-center justify-between bg-[#16161D]">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-white text-[#4285F4] font-bold flex items-center justify-center">G</div>
                        <div>
                          <div className="text-[14px] text-[#FAFAFA]">{email}</div>
                          <div className="text-[12px] text-[#71717A]">Connected via OAuth</div>
                        </div>
                      </div>
                      <button className="h-9 px-4 rounded-lg text-[#EF4444] hover:bg-[#EF4444]/10 text-[14px] font-medium transition-colors">
                        Disconnect
                      </button>
                    </div>

                    <button
                      onClick={markDirty}
                      className="mt-4 w-full h-10 rounded-lg border border-[#1F1F28] text-[#FAFAFA] hover:bg-[#1F1F28] transition-colors flex items-center justify-center gap-2 text-[14px]"
                    >
                      <Globe size={16} /> Import from app.trbm.shop
                    </button>

                    <details className="mt-6 group">
                      <summary className="cursor-pointer text-[14px] text-[#A1A1AA] flex items-center gap-2 hover:text-[#FAFAFA]">
                        <ChevronDown size={14} className="group-open:rotate-180 transition-transform" />
                        Use Service Account JSON instead
                      </summary>
                      <div className="mt-3 border border-dashed border-[#1F1F28] rounded-xl h-32 flex flex-col items-center justify-center text-[#71717A] hover:border-[#FF6B35]/40 transition-colors cursor-pointer">
                        <Upload size={24} className="mb-2" />
                        <div className="text-[13px]">Drop credentials.json</div>
                      </div>
                    </details>
                  </div>
                )}

                {tab === 'folders' && (
                  <div>
                    <div className="text-[18px] font-semibold text-[#FAFAFA]">Default Folder</div>
                    <div className="text-[13px] text-[#A1A1AA] mt-1">Where uploads go by default.</div>

                    <div className="mt-5 flex gap-2">
                      <input
                        value="TikTok Affiliate / 13sUXPBdGV..."
                        readOnly
                        className="flex-1 h-11 px-4 rounded-lg bg-[#16161D] border border-[#1F1F28] text-[14px] text-[#FAFAFA] font-mono"
                      />
                      <button className="h-11 px-4 rounded-lg border border-[#1F1F28] text-[#FAFAFA] hover:bg-[#1F1F28] text-[14px] flex items-center gap-2">
                        <Folder size={15} /> Browse
                      </button>
                    </div>

                    <div className="mt-8 text-[14px] font-semibold text-[#FAFAFA] mb-3">Pipeline Mappings</div>
                    <div className="border border-[#1F1F28] rounded-xl overflow-hidden">
                      <table className="w-full text-[13px]">
                        <thead className="bg-[#16161D] text-[11px] uppercase tracking-wide text-[#71717A]">
                          <tr>
                            <th className="text-left px-4 py-2.5">Pipeline</th>
                            <th className="text-left px-4 py-2.5">Folder</th>
                            <th className="text-right px-4 py-2.5">Auto-create</th>
                          </tr>
                        </thead>
                        <tbody>
                          {PIPELINES.map((p, i) => (
                            <tr key={p.name} className={i > 0 ? 'border-t border-[#1F1F28]' : ''}>
                              <td className="px-4 py-3 text-[#FAFAFA]">{p.name}</td>
                              <td className="px-4 py-3 text-[#A1A1AA] font-mono">{p.folder}</td>
                              <td className="px-4 py-3 text-right"><Toggle checked={true} onChange={markDirty} /></td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    <button className="mt-3 h-9 px-3 rounded-lg text-[#FF6B35] hover:bg-[#FF6B35]/10 text-[13px] flex items-center gap-1.5">
                      <Plus size={14} /> Add Pipeline Mapping
                    </button>
                  </div>
                )}

                {tab === 'rules' && (
                  <div>
                    <div className="text-[18px] font-semibold text-[#FAFAFA]">Sync Behavior</div>
                    <div className="text-[13px] text-[#A1A1AA] mt-1">How new files are handled.</div>

                    <div className="mt-5 border border-[#1F1F28] rounded-xl divide-y divide-[#1F1F28]">
                      {[
                        { key: 'autoSync', label: 'Auto-sync new videos', desc: 'Watch local folder and upload immediately.' },
                        { key: 'deleteLocal', label: 'Delete from local after sync', desc: 'Free disk after successful upload.' },
                        { key: 'compress', label: 'Compress before upload', desc: 'Re-encode large MP4 to save bandwidth.' },
                        { key: 'notifyErrors', label: 'Notify on sync errors', desc: 'Telegram + Zalo on failure.' },
                      ].map((r) => (
                        <div key={r.key} className="px-4 py-3 flex items-center justify-between">
                          <div>
                            <div className="text-[14px] text-[#FAFAFA]">{r.label}</div>
                            <div className="text-[12px] text-[#71717A] mt-0.5">{r.desc}</div>
                          </div>
                          <Toggle
                            checked={(rules as any)[r.key]}
                            onChange={(v) => { setRules({ ...rules, [r.key]: v }); markDirty(); }}
                          />
                        </div>
                      ))}
                    </div>

                    <div className="mt-6 text-[14px] font-semibold text-[#FAFAFA] mb-2">File Filters</div>
                    <div className="flex gap-2 flex-wrap">
                      {['.mp4', '.mov', '.json', '.srt', '.txt'].map((e) => (
                        <span key={e} className="h-7 px-3 rounded-full bg-[#16161D] border border-[#1F1F28] text-[12px] font-mono text-[#FAFAFA] flex items-center">
                          {e}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {tab === 'schedule' && (
                  <div>
                    <div className="text-[18px] font-semibold text-[#FAFAFA]">Sync Schedule</div>
                    <div className="text-[13px] text-[#A1A1AA] mt-1">When the watcher runs.</div>

                    <div className="mt-5 space-y-2">
                      {[
                        { id: 'realtime', label: 'Realtime (watcher)', desc: 'Upload immediately on file change.' },
                        { id: 'minutes', label: `Every ${interval} minutes`, desc: 'Periodic batch upload.' },
                        { id: 'daily', label: 'Daily at 03:00', desc: 'Run once per day.' },
                        { id: 'manual', label: 'Manual only', desc: 'Trigger via button.' },
                      ].map((opt) => (
                        <label
                          key={opt.id}
                          className={`flex items-start gap-3 px-4 py-3 rounded-xl border cursor-pointer transition-colors ${
                            schedule === opt.id ? 'border-[#FF6B35] bg-[#FF6B35]/5' : 'border-[#1F1F28] hover:bg-[#16161D]'
                          }`}
                        >
                          <input
                            type="radio" name="schedule" value={opt.id}
                            checked={schedule === opt.id}
                            onChange={() => { setSchedule(opt.id as any); markDirty(); }}
                            className="mt-1 accent-[#FF6B35]"
                          />
                          <div>
                            <div className="text-[14px] text-[#FAFAFA]">{opt.label}</div>
                            <div className="text-[12px] text-[#71717A] mt-0.5">{opt.desc}</div>
                          </div>
                        </label>
                      ))}
                    </div>

                    {schedule === 'minutes' && (
                      <div className="mt-4 flex items-center gap-3">
                        <label className="text-[13px] text-[#A1A1AA]">Every</label>
                        <input
                          type="number" min={5} max={1440}
                          value={interval}
                          onChange={(e) => { setInterval(Number(e.target.value)); markDirty(); }}
                          className="w-24 h-9 px-3 rounded-lg bg-[#16161D] border border-[#1F1F28] text-[#FAFAFA] text-[13px]"
                        />
                        <span className="text-[13px] text-[#A1A1AA]">minutes</span>
                      </div>
                    )}

                    <div className="mt-8 text-[12px] text-[#71717A]">Last synced: 2 minutes ago</div>
                  </div>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="h-14 px-8 border-t border-[#1F1F28] flex items-center justify-between shrink-0">
              <div className={`flex items-center gap-1.5 text-[13px] ${
                saving ? 'text-[#A1A1AA]' :
                dirty ? 'text-[#FACC15]' :
                saved ? 'text-[#22C55E]' :
                'text-[#71717A]'
              }`}>
                {saved && <Check size={14} />}
                {saving ? 'Saving...' : dirty ? 'Unsaved changes' : saved ? 'All changes saved' : 'No changes'}
              </div>
              <div className="flex gap-2">
                <button onClick={onClose} className="h-9 px-4 rounded-lg text-[#A1A1AA] hover:text-white hover:bg-[#1F1F28] text-[14px] transition-colors">
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  disabled={!dirty || saving}
                  className="h-9 px-5 rounded-lg bg-[#FF6B35] hover:bg-[#FF8159] disabled:bg-[#1F1F28] disabled:text-[#52525B] disabled:cursor-not-allowed text-white text-[14px] font-semibold transition-colors"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
