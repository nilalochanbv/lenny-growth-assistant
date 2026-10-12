import React, { useState } from 'react';
import { X, Server, Cloud, Database, RefreshCw, CheckCircle, AlertTriangle, Palette, Check } from 'lucide-react';
import type { HealthStatus, ModelsConfig } from '../../types';
import { useTheme } from '../../context/ThemeContext';
import { THEME_OPTIONS } from '../../types/theme';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  health: HealthStatus | null;
  modelsConfig: ModelsConfig | null;
  activeProvider: string;
  onChangeProvider: (provider: 'local' | 'cloud') => void;
  onTriggerReindex: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  health,
  modelsConfig,
  activeProvider,
  onChangeProvider,
  onTriggerReindex
}) => {
  const [reindexing, setReindexing] = useState(false);
  const { theme, setTheme } = useTheme();

  if (!isOpen) return null;

  const handleReindex = async () => {
    setReindexing(true);
    await onTriggerReindex();
    setTimeout(() => setReindexing(false), 2000);
  };

  const isLocalOnline = health?.local_provider.available ?? false;
  const isCloudAvailable = health?.cloud_provider.available ?? false;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Server size={18} color="#818cf8" />
            <h3 className="modal-title">Workspace Settings & Diagnostics</h3>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="modal-body">
          {/* Active Provider Selector */}
          <div className="form-group">
            <label className="form-label">Active Inference Engine</label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div 
                className={`prompt-card ${activeProvider === 'local' ? 'active' : ''}`}
                style={{ 
                  borderColor: activeProvider === 'local' ? 'var(--accent-primary)' : 'var(--border-subtle)',
                  cursor: 'pointer'
                }}
                onClick={() => onChangeProvider('local')}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600 }}>
                    <Server size={14} color="#818cf8" />
                    <span>Ollama (Local)</span>
                  </div>
                  {isLocalOnline ? (
                    <CheckCircle size={14} color="#10b981" />
                  ) : (
                    <AlertTriangle size={14} color="#f59e0b" />
                  )}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  {isLocalOnline ? `Online (${modelsConfig?.active_local_model || 'qwen2.5:0.5b'})` : 'Ollama Offline'}
                </div>
              </div>

              <div 
                className={`prompt-card ${activeProvider === 'cloud' ? 'active' : ''}`}
                style={{ 
                  borderColor: activeProvider === 'cloud' ? 'var(--accent-primary)' : 'var(--border-subtle)',
                  cursor: 'pointer'
                }}
                onClick={() => onChangeProvider('cloud')}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600 }}>
                    <Cloud size={14} color="#38bdf8" />
                    <span>Cloud LLM</span>
                  </div>
                  {isCloudAvailable ? (
                    <CheckCircle size={14} color="#10b981" />
                  ) : (
                    <AlertTriangle size={14} color="#94a3b8" />
                  )}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  {isCloudAvailable ? `Configured (${modelsConfig?.active_cloud_model})` : 'API Key Not Set'}
                </div>
              </div>
            </div>
            <span className="form-help">
              Local Ollama executes privately on this machine. Cloud provider connects via secure API keys in .env.
            </span>
          </div>

          {/* Theme & Atmosphere Selector */}
          <div className="form-group" style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px', margin: 0 }}>
                <Palette size={14} color="var(--accent-primary)" />
                <span>Atmosphere & Studio Theme</span>
              </label>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Live preview</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(170px, 1fr))', gap: '10px' }}>
              {THEME_OPTIONS.map((t) => {
                const isCurrent = t.id === theme;
                return (
                  <div
                    key={t.id}
                    className={`prompt-card theme-modal-card ${isCurrent ? 'active' : ''}`}
                    style={{
                      borderColor: isCurrent ? 'var(--border-active)' : 'var(--border-subtle)',
                      boxShadow: isCurrent ? '0 0 16px var(--accent-light), inset 0 1px 0 rgba(255,255,255,0.06)' : 'none',
                      cursor: 'pointer',
                      padding: '12px 14px',
                      position: 'relative',
                      overflow: 'hidden',
                      transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
                      borderRadius: 'var(--radius-md)'
                    }}
                    onClick={() => setTheme(t.id)}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <div
                        style={{
                          width: '16px',
                          height: '16px',
                          borderRadius: '50%',
                          background: t.gradient,
                          boxShadow: '0 2px 6px rgba(0,0,0,0.4)',
                          border: '1px solid rgba(255,255,255,0.4)',
                          flexShrink: 0
                        }}
                      />
                      {isCurrent ? (
                        <Check size={14} color="var(--accent-primary)" />
                      ) : (
                        t.isLight && <span style={{ fontSize: '9px', fontWeight: 600, opacity: 0.6 }}>LIGHT</span>
                      )}
                    </div>
                    <div style={{ fontWeight: 600, fontSize: '12.5px', color: 'var(--text-main)', marginBottom: '3px' }}>
                      {t.name}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', lineHeight: '1.3' }}>
                      {t.tagline}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Database & Transcript Index Diagnostics */}
          <div className="form-group" style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Database size={14} />
                <span>Transcript Knowledge Base</span>
              </label>
              <button 
                className="action-btn" 
                onClick={handleReindex}
                disabled={reindexing}
                style={{ border: '1px solid var(--border-subtle)', padding: '4px 10px' }}
              >
                <RefreshCw size={12} className={reindexing ? 'animate-spin' : ''} />
                <span>{reindexing ? 'Re-indexing...' : 'Refresh Index'}</span>
              </button>
            </div>

            <div style={{ background: 'var(--bg-elevated)', padding: '12px', borderRadius: 'var(--radius-sm)', fontSize: '13px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ color: 'var(--text-secondary)' }}>PostgreSQL Status:</span>
                <span style={{ color: health?.database.connected ? '#10b981' : '#ef4444', fontWeight: 500 }}>
                  {health?.database.connected ? 'Connected (Port 5432)' : 'Disconnected'}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Indexed Chunks:</span>
                <span style={{ fontWeight: 600 }}>{health?.database.total_indexed_chunks.toLocaleString() || '0'}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Vector Dimension:</span>
                <span style={{ fontWeight: 500, color: '#818cf8' }}>256-dim Semantic Feature Vectors</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
