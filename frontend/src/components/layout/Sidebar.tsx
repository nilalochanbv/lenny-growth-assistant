import { useState } from 'react';
import { 
  Plus, 
  MessageSquare, 
  Trash2, 
  Settings as SettingsIcon, 
  Search, 
  Database,
  ChevronLeft
} from 'lucide-react';
import type { Session } from '../../types';
import { useTheme } from '../../context/ThemeContext';

interface SidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string) => void;
  onOpenSettings: () => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  totalIndexedChunks?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  onOpenSettings,
  isCollapsed,
  onToggleCollapse,
  totalIndexedChunks = 6479
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const { cycleTheme, currentThemeOption } = useTheme();

  const filteredSessions = sessions.filter(s => 
    s.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="brand-wrapper">
          <div className="brand-logo">L</div>
          <div>
            <div className="brand-title">Lenny Growth</div>
          </div>
          <span className="brand-badge">PRO</span>
        </div>
        <button 
          className="toggle-sidebar-btn" 
          onClick={onToggleCollapse} 
          title="Collapse sidebar"
        >
          <ChevronLeft size={16} />
        </button>
      </div>

      <button className="new-chat-btn" onClick={onNewSession}>
        <Plus size={16} />
        <span>New Conversation</span>
      </button>

      <div className="search-box">
        <Search size={14} className="search-icon" />
        <input 
          type="text" 
          className="search-input" 
          placeholder="Filter conversations..." 
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div className="session-list">
        {filteredSessions.length === 0 ? (
          <div style={{ padding: '20px 10px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '12px' }}>
            {sessions.length === 0 ? 'No conversations yet' : 'No matching sessions'}
          </div>
        ) : (
          filteredSessions.map((s) => (
            <div 
              key={s.id} 
              className={`session-item ${s.id === activeSessionId ? 'active' : ''}`}
              onClick={() => onSelectSession(s.id)}
            >
              <div className="session-title-wrapper">
                <MessageSquare size={14} style={{ flexShrink: 0, opacity: 0.7 }} />
                <span>{s.title}</span>
              </div>
              <button 
                className="delete-session-btn" 
                title="Delete conversation"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteSession(s.id);
                }}
              >
                <Trash2 size={13} />
              </button>
            </div>
          ))
        )}
      </div>

      <div className="sidebar-footer">
        <div className="status-indicator">
          <div className="status-dot" />
          <span style={{ fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Database size={11} style={{ opacity: 0.7 }} />
            {totalIndexedChunks.toLocaleString()} chunks
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <button 
            className="settings-btn" 
            title={`Atmosphere: ${currentThemeOption.name} (Click to toggle)`}
            onClick={cycleTheme}
            aria-label="Toggle theme atmosphere"
          >
            <span 
              style={{ 
                width: '13px', 
                height: '13px', 
                borderRadius: '50%', 
                background: currentThemeOption.gradient, 
                display: 'inline-block',
                border: '1px solid rgba(255, 255, 255, 0.4)',
                boxShadow: '0 0 8px var(--accent-light)',
                transition: 'all 0.2s ease'
              }} 
            />
          </button>
          <button 
            className="settings-btn" 
            title="Settings & Diagnostics"
            onClick={onOpenSettings}
            aria-label="Settings"
          >
            <SettingsIcon size={15} />
          </button>
        </div>
      </div>
    </aside>
  );
};
