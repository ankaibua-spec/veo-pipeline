/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import {
  Home,
  Video,
  Image as ImageIcon,
  LayoutList,
  History,
  Settings,
  Menu,
  Play,
  Plus,
  Search,
  Filter,
  MoreVertical,
  CheckCircle2,
  AlertCircle,
  Clock,
  Zap,
  Cpu,
  HardDrive,
  Users,
  LogOut,
  Maximize2,
  RefreshCw,
  Sparkles,
  ChevronDown,
  Trash2,
  FileText,
  Key,
  Cloud
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import LicenseModal from './screens/LicenseModal';
import OnboardingModal from './screens/OnboardingModal';
import DriveSyncModal from './screens/DriveSyncModal';

// Nguon duy nhat cho version string — doc tu package.json qua vite.config.ts define
const APP_VERSION: string = import.meta.env.VITE_APP_VERSION ?? '0.0.0';

// Types
type Page = 'home' | 'text2video' | 'image2video' | 'bulk-login' | 'queue' | 'history' | 'settings';

interface StatProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: string;
  progress?: number;
  badge?: string;
}

// Components
const StatCard = ({ label, value, icon, trend, progress, badge }: StatProps) => (
  <div className="bg-[#252525] border border-[#404040] rounded-xl p-5 shadow-lg flex flex-col gap-2">
    <div className="flex justify-between items-center text-[#A0A0A0] text-xs font-semibold uppercase tracking-wider">
      {label}
      <div className="text-blue-400">{icon}</div>
    </div>
    <div className="flex items-baseline gap-2 mt-1">
      <div className="text-2xl font-bold text-white">{value}</div>
      {trend && <div className="text-[11px] text-emerald-400 flex items-center font-medium">{trend}</div>}
      {badge && (
        <div className="text-[10px] bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2 py-0.5 rounded-full font-bold ml-2">
          {badge}
        </div>
      )}
    </div>
    {progress !== undefined && (
      <div className="w-full h-1.5 bg-[#3A3A3A] rounded-full mt-2 overflow-hidden">
        <div 
          className="h-full bg-amber-500 rounded-full" 
          style={{ width: `${progress}%` }}
        />
      </div>
    )}
  </div>
);

// --- Pages ---

const Dashboard = () => (
  <div className="space-y-8">
    <header className="mb-6">
      <h2 className="text-2xl font-bold text-white tracking-tight">Trang chủ</h2>
      <p className="text-sm text-[#A0A0A0] mt-1">Tổng quan hệ thống video pipeline</p>
    </header>

    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      <StatCard label="Videos Today" value="0" icon={<Video size={18} />} trend="—" />
      <StatCard label="This Month" value="0" icon={<Clock size={18} />} trend="videos" />
      <StatCard label="Credits Left" value="—" icon={<Zap size={18} />} trend="not connected" />
      <StatCard label="Queue Status" value="0" icon={<LayoutList size={18} />} badge="Idle" />
    </div>

    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        {/* Quick Actions */}
        <section className="bg-[#252525] border border-[#404040] rounded-xl p-6">
          <h3 className="text-sm font-bold text-white mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <button className="h-32 bg-[#3A3A3A] hover:bg-[#404040] border border-[#404040] transition-all rounded-lg flex flex-col items-center justify-center gap-3 group">
              <Video className="text-blue-400 group-hover:scale-110 transition-transform" size={32} />
              <span className="text-sm font-medium text-white">Text to Video</span>
            </button>
            <button className="h-32 bg-[#3A3A3A] hover:bg-[#404040] border border-[#404040] transition-all rounded-lg flex flex-col items-center justify-center gap-3 group">
              <ImageIcon className="text-blue-400 group-hover:scale-110 transition-transform" size={32} />
              <span className="text-sm font-medium text-white">Image to Video</span>
            </button>
          </div>
        </section>

        {/* Recent Table */}
        <section className="bg-[#252525] border border-[#404040] rounded-xl overflow-hidden">
          <div className="p-6 border-b border-[#404040]">
            <h3 className="text-sm font-bold text-white">Recent Generations</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-[#2B2B2B] text-[#A0A0A0] text-[11px] font-bold uppercase tracking-wider">
                  <th className="px-6 py-3">Project Name</th>
                  <th className="px-6 py-3">Type</th>
                  <th className="px-6 py-3 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="text-xs text-[#E0E2EA] font-medium">
                <tr>
                  <td colSpan={3} className="px-6 py-12 text-center text-[#707070]">
                    No videos generated yet. Click <span className="text-blue-400">Text to Video</span> to start.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>

      <div className="space-y-6">
        <section className="bg-[#252525] border border-[#404040] rounded-xl p-6">
          <h3 className="text-sm font-bold text-white mb-4">System Status</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center text-xs">
              <span className="text-[#A0A0A0]">Backend</span>
              <span className="flex items-center gap-1.5 text-[#707070] font-medium">
                <span className="w-2 h-2 rounded-full bg-[#707070]"></span>
                Not connected
              </span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-[#A0A0A0]">Drive</span>
              <span className="flex items-center gap-1.5 text-[#707070] font-medium">
                <span className="w-2 h-2 rounded-full bg-[#707070]"></span>
                Not connected
              </span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-[#A0A0A0]">License</span>
              <span className="flex items-center gap-1.5 text-amber-400 font-medium">
                <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                Not activated
              </span>
            </div>
          </div>
        </section>

        <section className="bg-gradient-to-br from-blue-600/20 to-[#1F1F1F] border border-[#404040] rounded-xl p-6 min-h-[160px] flex flex-col justify-end">
          <span className="text-[10px] font-mono text-blue-400 mb-1">v{APP_VERSION}</span>
          <h3 className="text-lg font-bold text-white tracking-tight">Engine Ready</h3>
        </section>
      </div>
    </div>
  </div>
);

const TextToVideo = () => (
  <div className="max-w-5xl mx-auto space-y-8">
    <header className="mb-6">
      <h2 className="text-2xl font-bold text-white tracking-tight">Văn bản → Video</h2>
      <p className="text-sm text-[#A0A0A0] mt-1">Tạo video từ mô tả văn bản chi tiết</p>
    </header>

    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div className="lg:col-span-8 space-y-6">
        <div className="bg-[#252525] border border-[#404040] rounded-xl p-6 shadow-xl">
          <div className="flex justify-between items-center mb-4">
            <label className="text-xs font-bold text-white uppercase tracking-wider">Prompt</label>
            <span className="text-[10px] bg-[#3A3A3A] text-[#A0A0A0] px-2 py-0.5 rounded font-bold">Required</span>
          </div>
          <textarea 
            className="w-full h-48 bg-[#3A3A3A] border border-[#404040] rounded-lg p-4 text-sm text-white placeholder-[#707070] resize-none focus:outline-none focus:border-blue-500 transition-colors"
            placeholder="Mô tả chi tiết video bạn muốn tạo. (Ví dụ: Một con rồng bay qua thành phố cyberpunk vào ban đêm, neon sáng rực, góc quay flycam...)"
          />
          <div className="mt-4 flex justify-end">
            <button className="bg-[#3A3A3A] hover:bg-[#404040] border border-[#404040] text-white text-xs font-bold px-4 py-2 rounded-lg flex items-center gap-2 transition-all">
              <Sparkles size={14} className="text-blue-400" />
              Enhance Prompt
            </button>
          </div>
        </div>

        <div className="bg-[#252525] border border-[#404040] rounded-xl p-6 shadow-xl">
          <label className="text-xs font-bold text-white uppercase tracking-wider mb-2 block">Negative Prompt</label>
          <p className="text-[11px] text-[#A0A0A0] mb-4">Những gì không muốn xuất hiện trong video</p>
          <textarea 
            className="w-full h-20 bg-[#3A3A3A] border border-[#404040] rounded-lg p-4 text-sm text-white placeholder-[#707070] resize-none focus:outline-none focus:border-blue-500 transition-colors"
            placeholder="blur, low quality, watermark, text..."
          />
        </div>
      </div>

      <div className="lg:col-span-4 space-y-6">
        <div className="bg-[#252525] border border-[#404040] rounded-xl p-6 shadow-xl space-y-6">
          <h3 className="text-sm font-bold text-white border-b border-[#404040] pb-3">Cài đặt Video</h3>
          
          <div className="space-y-2">
            <label className="text-xs font-medium text-[#A0A0A0]">Model</label>
            <div className="relative">
              <select className="w-full appearance-none bg-[#3A3A3A] border border-[#404040] rounded text-xs p-2.5 text-white focus:outline-none focus:border-blue-500">
                <option>VEO-V1-Alpha</option>
                <option>VEO-V2-Beta</option>
                <option>Stable Video Diffusion</option>
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 text-[#707070]" size={14} />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-medium text-[#A0A0A0]">Aspect Ratio</label>
            <div className="grid grid-cols-3 gap-2">
              <button className="bg-blue-500 text-white border border-blue-400 py-3 rounded-lg flex flex-col items-center justify-center gap-1">
                <Maximize2 size={14} />
                <span className="text-[10px] font-bold">16:9</span>
              </button>
              <button className="bg-[#3A3A3A] text-[#A0A0A0] border border-[#404040] py-3 rounded-lg flex flex-col items-center justify-center gap-1 hover:text-white transition-colors">
                <Maximize2 size={14} className="rotate-90" />
                <span className="text-[10px] font-bold">9:16</span>
              </button>
              <button className="bg-[#3A3A3A] text-[#A0A0A0] border border-[#404040] py-3 rounded-lg flex flex-col items-center justify-center gap-1 hover:text-white transition-colors">
                <Maximize2 size={14} className="scale-75" />
                <span className="text-[10px] font-bold">1:1</span>
              </button>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <label className="text-xs font-medium text-[#A0A0A0]">Duration (seconds)</label>
              <span className="text-[11px] font-mono text-white">4s</span>
            </div>
            <input type="range" className="w-full h-1.5 bg-[#3A3A3A] rounded-full appearance-none cursor-pointer accent-blue-500" />
          </div>

          <div className="pt-4 border-t border-[#404040]">
            <button className="w-full bg-[#FF6B35] hover:bg-[#ff8255] text-white text-sm font-bold py-3 rounded-lg flex items-center justify-center gap-2 shadow-[0_4px_15px_rgba(255,107,53,0.3)] transition-all active:scale-[0.98]">
              <Play size={16} fill="currentColor" />
              Tạo video
            </button>
            <p className="text-[10px] text-center text-[#707070] mt-3 flex items-center justify-center gap-1 uppercase tracking-wider">
              <Zap size={10} className="text-amber-500" fill="currentColor" />
              Cost: 15 credits
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const HistoryPage = () => (
  <div className="space-y-8">
    <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-[#404040] pb-6">
      <div className="space-y-1">
        <h2 className="text-2xl font-bold text-white tracking-tight">Lịch sử</h2>
        <p className="text-sm text-[#A0A0A0]">Danh sách video đã hoàn thành của bạn</p>
      </div>
      <div className="flex gap-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#707070]" size={16} />
          <input 
            className="bg-[#3A3A3A] border border-[#404040] rounded-lg pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-blue-500 w-full sm:w-64"
            placeholder="Find by prompt..."
          />
        </div>
        <button className="bg-[#3A3A3A] border border-[#404040] p-2 rounded-lg text-white">
          <Filter size={18} />
        </button>
      </div>
    </div>

    <div className="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-6">
      {[1, 2, 3, 4, 5].map((i) => (
        <motion.div 
          key={i}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
          className="group cursor-pointer"
        >
          <div className="aspect-[9/16] bg-[#252525] border border-[#404040] rounded-2xl overflow-hidden relative shadow-lg group-hover:border-blue-500 transition-all">
            <img 
              src={`https://picsum.photos/400/700?random=${i}`} 
              alt="Thumbnail" 
              className="w-full h-full object-cover opacity-60 group-hover:opacity-80 transition-opacity"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent flex flex-col justify-end p-4">
              <div className="text-[10px] text-blue-400 font-bold mb-1 uppercase tracking-wider flex items-center gap-1">
                <Video size={10} />
                VEO 2.0
              </div>
              <p className="text-xs text-white font-medium line-clamp-2">Cyberpunk city rainy night neon lights...</p>
              <div className="flex justify-between items-center mt-3 text-[10px] text-[#A0A0A0]">
                <span className="flex items-center gap-1"><Clock size={10} /> 2 hours ago</span>
                <span className="bg-black/50 px-1.5 py-0.5 rounded backdrop-blur">00:08</span>
              </div>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  </div>
);

const BulkLogin = () => (
  <div className="space-y-8">
    <header className="mb-6">
      <h2 className="text-2xl font-bold text-white tracking-tight">Đăng nhập hàng loạt</h2>
      <p className="text-sm text-[#A0A0A0] mt-1">Quản lý và đăng nhập tự động nhiều tài khoản</p>
    </header>

    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-1 space-y-6">
        <section className="bg-[#252525] border border-[#404040] rounded-xl p-6 shadow-xl space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white">Dữ liệu đầu vào</h3>
            <p className="text-[11px] text-[#707070] mt-1">Định dạng: email|password</p>
          </div>
          <div className="space-y-2">
            <label className="text-[10px] uppercase font-bold text-[#A0A0A0] tracking-wider">Tải lên tập tin</label>
            <div className="border-2 border-dashed border-[#404040] rounded-lg p-6 flex flex-col items-center justify-center gap-2 hover:border-blue-500 cursor-pointer transition-colors bg-[#333]/30">
              <Plus className="text-[#707070]" size={24} />
              <span className="text-[11px] font-bold text-white">Chọn file .txt</span>
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-[10px] uppercase font-bold text-[#A0A0A0] tracking-wider">Hoặc dán trực tiếp</label>
            <textarea 
              className="w-full h-40 bg-[#3A3A3A] border border-[#404040] rounded-lg p-3 text-xs font-mono text-white placeholder-[#707070] resize-none focus:outline-none focus:border-blue-500 transition-colors"
              placeholder="user1@example.com|pass123&#10;user2@example.com|pass456"
            />
          </div>
          <button className="w-full bg-[#3A3A3A] hover:bg-[#404040] border border-[#404040] text-white text-xs font-bold py-2.5 rounded-lg flex items-center justify-center gap-2 transition-all">
            <Plus size={14} /> Thêm vào danh sách
          </button>
        </section>
      </div>

      <div className="lg:col-span-2 space-y-6">
        <section className="bg-[#252525] border border-[#404040] rounded-xl overflow-hidden shadow-xl">
          <div className="p-6 border-b border-[#404040] flex justify-between items-center bg-[#2B2B2B]">
            <div>
              <h3 className="text-sm font-bold text-white">Danh sách tài khoản</h3>
              <p className="text-[11px] text-[#707070] mt-1">Tổng cộng: 4 tài khoản</p>
            </div>
            <div className="flex gap-2">
              <button className="p-2 text-[#A0A0A0] hover:text-white"><Search size={16} /></button>
              <button className="p-2 text-[#A0A0A0] hover:text-rose-400"><Trash2 size={16} /></button>
            </div>
          </div>
          <div className="overflow-x-auto h-[320px]">
            <table className="w-full text-left">
              <thead className="bg-[#1c2026] text-[#A0A0A0] text-[10px] font-bold uppercase tracking-wider sticky top-0 z-10 shadow-sm">
                <tr>
                  <th className="px-6 py-3 w-12">#</th>
                  <th className="px-6 py-3">Email</th>
                  <th className="px-6 py-3">Profile</th>
                  <th className="px-6 py-3 text-right">Trạng thái</th>
                </tr>
              </thead>
              <tbody className="text-[11px] text-[#E0E2EA] divide-y divide-[#404040] font-medium">
                <tr className="hover:bg-[#333] transition-colors">
                  <td className="px-6 py-3 text-[#707070]">1</td>
                  <td className="px-6 py-3">john.doe@example.com</td>
                  <td className="px-6 py-3 text-[#A0A0A0]">Profile_001</td>
                  <td className="px-6 py-3 text-right">
                    <span className="bg-amber-500/10 text-amber-500 border border-amber-500/20 px-2 py-1 rounded text-[9px] font-bold">Pending</span>
                  </td>
                </tr>
                <tr className="hover:bg-[#333] transition-colors">
                  <td className="px-6 py-3 text-[#707070]">2</td>
                  <td className="px-6 py-3">jane.smith@example.com</td>
                  <td className="px-6 py-3 text-[#A0A0A0]">Profile_002</td>
                  <td className="px-6 py-3 text-right">
                    <span className="bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-1 rounded text-[9px] font-bold italic animate-pulse">Running</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section className="bg-black/40 border border-[#404040] rounded-xl overflow-hidden font-mono text-[11px]">
          <div className="bg-[#2B2B2B] px-4 py-2 border-b border-[#404040] flex items-center justify-between">
            <span className="text-[#A0A0A0] uppercase tracking-widest text-[9px] font-bold">Execution Log</span>
            <div className="flex gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-rose-500"></div>
              <div className="w-1.5 h-1.5 rounded-full bg-amber-500"></div>
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
            </div>
          </div>
          <div className="p-4 space-y-1 h-24 overflow-y-auto text-[#A0A0A0]">
            <div><span className="text-blue-500">[10:30:05]</span> Initializing chrome instances...</div>
            <div><span className="text-white">[10:30:12]</span> Navigating to login portal...</div>
          </div>
        </section>
      </div>
    </div>
  </div>
);

const SettingsPage = () => (
  <div className="max-w-5xl mx-auto space-y-8">
    <header className="mb-6">
      <h2 className="text-2xl font-bold text-white tracking-tight">Cấu hình hệ thống</h2>
      <p className="text-sm text-[#A0A0A0] mt-1">Quản lý cấu hình ứng dụng và các tích hợp API</p>
    </header>

    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        <section className="bg-[#252525] border border-[#404040] rounded-xl p-8 shadow-xl space-y-6">
           <div className="flex items-center gap-2 text-blue-400 font-bold text-[10px] uppercase tracking-widest">
            <HardDrive size={14} /> Đường dẫn đầu ra
          </div>
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-[11px] font-medium text-[#707070]">Thư mục lưu video</label>
              <div className="flex gap-2">
                <input readOnly value="D:\VEOPipeline\Outputs\Videos" className="flex-1 bg-[#3A3A3A] border border-[#404040] rounded-lg px-4 py-2 text-xs font-mono text-white opacity-80" />
                <button className="bg-[#3A3A3A] border border-[#404040] text-white text-[11px] font-bold px-4 rounded-lg">Chọn</button>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-[#252525] border border-[#404040] rounded-xl p-8 shadow-xl space-y-6">
          <div className="flex items-center gap-2 text-blue-400 font-bold text-[10px] uppercase tracking-widest">
            <Sparkles size={14} /> Tích hợp
          </div>
          <div className="space-y-5">
            <div className="flex items-center justify-between p-4 bg-[#2B2B2B] rounded-xl border border-[#404040]">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center p-2 text-emerald-600 font-bold">G</div>
                <div>
                  <h4 className="text-sm font-bold text-white">Google Drive</h4>
                  <p className="text-[10px] text-[#707070]">Chưa kết nối</p>
                </div>
              </div>
              <button className="bg-[#3A3A3A] border border-[#404040] text-white text-xs font-bold px-5 py-2 rounded-lg">Kết nối</button>
            </div>
          </div>
        </section>
      </div>

      <div className="lg:col-span-1 space-y-6">
        <section className="bg-gradient-to-br from-blue-600/10 to-[#1F1F1F] border border-[#404040] rounded-xl p-6 shadow-xl space-y-5">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <CheckCircle2 size={16} className="text-blue-400" /> Khối Tài khoản
          </h3>
          <div className="space-y-4">
            <div>
              <p className="text-[9px] text-[#707070] uppercase font-bold tracking-widest mb-1.5">Bản quyền</p>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono text-white bg-[#3A3A3A] px-2 py-1 rounded border border-[#404040]">v{APP_VERSION} Comm</span>
                <span className="text-[9px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">Active</span>
              </div>
            </div>
            <button className="w-full bg-blue-600 text-white text-xs font-bold py-2.5 rounded-lg active:scale-95 transition-all">Gia hạn ngay</button>
          </div>
        </section>
      </div>
    </div>
  </div>
);

const QueuePage = () => (
  <div className="space-y-8">
    <div className="flex justify-between items-end mb-6">
      <div className="space-y-1">
        <h2 className="text-2xl font-bold text-white tracking-tight">Hàng đợi</h2>
        <p className="text-sm text-[#A0A0A0]">Quản lý tiến trình xử lý. Active jobs: <span className="text-blue-400 font-mono font-bold">12</span></p>
      </div>
      <button className="bg-[#3A3A3A] border border-[#404040] text-white text-xs font-bold px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-[#404040] transition-all">
        <RefreshCw size={14} />
        Refresh
      </button>
    </div>

    <div className="bg-[#252525] border border-[#404040] rounded-2xl overflow-hidden shadow-2xl">
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-[#2B2B2B] text-[#A0A0A0] text-[11px] font-bold uppercase tracking-wider">
              <th className="px-6 py-4 w-24">ID</th>
              <th className="px-6 py-4 w-32">Type</th>
              <th className="px-6 py-4">Prompt</th>
              <th className="px-6 py-4 w-48">Progress</th>
              <th className="px-6 py-4 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="text-xs text-[#E0E2EA] font-medium divide-y divide-[#404040] font-mono">
            {[1, 2, 3].map((i) => (
              <tr key={i} className="hover:bg-[#333] transition-colors group">
                <td className="px-6 py-6 text-blue-400">#8a9b2c</td>
                <td className="px-6 py-6 text-[#A0A0A0]">Text2Vid</td>
                <td className="px-6 py-6 max-w-xs truncate text-[#A0A0A0] group-hover:text-white transition-colors">A cinematic shot of a cyberpunk city in the rain...</td>
                <td className="px-6 py-6">
                  <div className="flex items-center gap-3">
                    <div className="flex-1 h-2 bg-[#3A3A3A] rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500 transition-all duration-1000" style={{ width: '45%' }}></div>
                    </div>
                    <span className="text-[#A0A0A0] w-8">45%</span>
                  </div>
                </td>
                <td className="px-6 py-6 text-right">
                  <span className="inline-flex items-center gap-1.5 bg-blue-500/10 text-blue-400 border border-blue-500/20 px-3 py-1 rounded-full text-[10px] font-bold">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"></div>
                    Running
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  </div>
);

// --- Main Layout ---

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home');
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [licenseOpen, setLicenseOpen] = useState(false);
  const [onboardingOpen, setOnboardingOpen] = useState(false);
  const [driveOpen, setDriveOpen] = useState(false);

  const NavItem = ({ id, label, icon, activeIcon }: { id: Page, label: string, icon: React.ReactNode, activeIcon?: React.ReactNode }) => {
    const isActive = currentPage === id;
    return (
      <button 
        onClick={() => setCurrentPage(id)}
        className={`w-full flex items-center gap-3 px-4 py-2.5 transition-all text-sm antialiased relative group ${
          isActive 
            ? 'bg-blue-600 text-white' 
            : 'text-[#A0A0A0] hover:bg-[#333] hover:text-white'
        }`}
      >
        {isActive && (
          <motion.div 
            layoutId="active-indicator"
            className="absolute left-0 top-0 bottom-0 w-1 bg-blue-400 shadow-[0_0_10px_rgba(96,165,250,0.5)]" 
          />
        )}
        <span className={`${isActive ? 'text-white' : 'group-hover:text-white'} transition-colors`}>
          {isActive && activeIcon ? activeIcon : icon}
        </span>
        <span className="font-medium tracking-tight">{label}</span>
      </button>
    );
  };

  return (
    <div className="min-h-screen bg-[#1F1F1F] text-[#E0E2EA] flex font-sans selection:bg-blue-500 selection:text-white">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 bg-[#1c2026] border-r border-[#404040] flex flex-col z-50 transition-all duration-300 ${isSidebarOpen ? 'w-64' : 'w-0 -translate-x-full lg:w-20 lg:translate-x-0'}`}>
        <div className="p-6 border-b border-[#404040] shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600 border border-blue-400 shadow-[0_0_15px_rgba(0,120,212,0.4)] flex items-center justify-center shrink-0">
              <Video className="text-white" size={20} />
            </div>
            {isSidebarOpen && (
              <div className="flex flex-col overflow-hidden">
                <span className="text-sm font-black text-white tracking-[1px] uppercase truncate">VEO Pro</span>
                <span className="text-[10px] text-[#707070] font-mono uppercase tracking-widest mt-0.5">Pipeline</span>
              </div>
            )}
          </div>
          {isSidebarOpen && (
            <div className="mt-6 bg-[#2B2B2B] rounded-lg p-3 border border-[#404040]">
              <div className="text-[10px] text-[#707070] uppercase font-bold tracking-wider mb-1">Developer</div>
              <div className="text-[11px] text-[#A0A0A0] font-medium truncate">Truong Hoa</div>
              <div className="text-[11px] text-[#A0A0A0] font-medium opacity-60 mt-0.5">0345431884</div>
            </div>
          )}
        </div>

        <nav className="flex-1 py-4 flex flex-col gap-0.5 overflow-y-auto overflow-x-hidden transition-all duration-300">
          <NavItem id="home" label={isSidebarOpen ? "Home" : ""} icon={<Home size={18} />} />
          <NavItem id="text2video" label={isSidebarOpen ? "Text to Video" : ""} icon={<Video size={18} />} activeIcon={<Video size={18} fill="currentColor" />} />
          <NavItem id="image2video" label={isSidebarOpen ? "Image to Video" : ""} icon={<ImageIcon size={18} />} />
          <NavItem id="bulk-login" label={isSidebarOpen ? "Bulk Login" : ""} icon={<Users size={18} />} />
          <NavItem id="queue" label={isSidebarOpen ? "Queue" : ""} icon={<LayoutList size={18} />} />
          <NavItem id="history" label={isSidebarOpen ? "History" : ""} icon={<History size={18} />} />
        </nav>

        <div className="p-4 border-t border-[#404040] space-y-0.5 transition-all duration-300">
          <NavItem id="settings" label={isSidebarOpen ? "Settings" : ""} icon={<Settings size={18} />} />
          {isSidebarOpen && (
            <button className="w-full flex items-center gap-3 px-4 py-2.5 text-[#A0A0A0] hover:bg-rose-500/10 hover:text-rose-400 transition-all text-sm rounded-lg group">
              <LogOut size={18} className="group-hover:text-rose-400" />
              <span className="font-medium">Logout</span>
            </button>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <div className={`flex-1 flex flex-col transition-all duration-300 ${isSidebarOpen ? 'lg:ml-64' : 'lg:ml-20'}`}>
        {/* Top Header */}
        <header className="h-14 bg-[#1c2026]/95 backdrop-blur-md border-b border-[#404040] flex items-center justify-between px-6 sticky top-0 z-40">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setSidebarOpen(!isSidebarOpen)}
              className="text-[#707070] hover:text-white transition-colors p-1"
            >
              <Menu size={20} />
            </button>
            <h1 className="text-sm font-bold text-blue-500 uppercase tracking-[1px]">Project Dashboard</h1>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 bg-[#2B2B2B] border border-[#404040] px-3 py-1.5 rounded-lg">
              <div className="w-2 h-2 rounded-full bg-emerald-400"></div>
              <span className="text-[11px] font-bold text-[#A0A0A0]">ONLINE</span>
            </div>
            <button
              onClick={() => setDriveOpen(true)}
              title="Drive Sync Settings"
              className="w-9 h-9 rounded-lg flex items-center justify-center text-[#A0A0A0] hover:text-white hover:bg-[#2B2B2B] transition-colors"
            >
              <Cloud size={16} />
            </button>
            <button
              onClick={() => setLicenseOpen(true)}
              title="License"
              className="w-9 h-9 rounded-lg flex items-center justify-center text-[#A0A0A0] hover:text-white hover:bg-[#2B2B2B] transition-colors"
            >
              <Key size={16} />
            </button>
            <button
              onClick={() => setOnboardingOpen(true)}
              title="Setup Wizard"
              className="w-9 h-9 rounded-lg flex items-center justify-center text-[#A0A0A0] hover:text-white hover:bg-[#2B2B2B] transition-colors"
            >
              <Sparkles size={16} />
            </button>
            <button className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-black px-4 h-9 rounded-lg flex items-center gap-2 shadow-lg shadow-blue-600/20 transition-all uppercase tracking-wide">
              <Plus size={14} />
              Generate
            </button>
          </div>
        </header>

        {/* Page Area */}
        <main className="flex-1 p-8 sm:p-10 lg:p-12 overflow-y-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentPage}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              transition={{ duration: 0.2 }}
            >
              {currentPage === 'home' && <Dashboard />}
              {currentPage === 'text2video' && <TextToVideo />}
              {currentPage === 'image2video' && (
                <div className="flex items-center justify-center h-64 text-[#A0A0A0] text-sm">
                  Image-to-Video coming soon
                </div>
              )}
              {currentPage === 'bulk-login' && <BulkLogin />}
              {currentPage === 'queue' && <QueuePage />}
              {currentPage === 'history' && <HistoryPage />}
              {currentPage === 'settings' && <SettingsPage />}
            </motion.div>
          </AnimatePresence>
        </main>

        {/* Footer info bar */}
        <footer className="h-8 border-t border-[#404040] bg-[#1c2026] flex items-center justify-between px-6 shrink-0">
          <div className="text-[10px] font-mono text-[#707070] uppercase tracking-widest">
            VEO Pipeline Pro v{APP_VERSION} | System Status: <span className="text-emerald-500 font-bold">Operational</span>
          </div>
          <div className="flex gap-6 text-[10px] font-mono text-[#707070] uppercase tracking-widest">
            <button className="hover:text-blue-400 transition-colors">Support</button>
            <button className="hover:text-blue-400 transition-colors">API Docs</button>
          </div>
        </footer>
      </div>

      <LicenseModal open={licenseOpen} onClose={() => setLicenseOpen(false)} />
      <OnboardingModal open={onboardingOpen} onClose={() => setOnboardingOpen(false)} />
      <DriveSyncModal open={driveOpen} onClose={() => setDriveOpen(false)} />
    </div>
  );
}
