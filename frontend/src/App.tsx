import { useState, useEffect, useRef } from 'react';
import { Menu, AlertCircle } from 'lucide-react';
import type { Session, Message, Artifact, Citation, HealthStatus, ModelsConfig, ModelInfo } from './types';
import { api } from './services/api';
import { Sidebar } from './components/layout/Sidebar';
import { ThemeSwitcher } from './components/layout/ThemeSwitcher';
import { EmptyState } from './components/chat/EmptyState';
import { MessageItem } from './components/chat/MessageItem';
import { Composer } from './components/chat/Composer';
import { ArtifactViewer } from './components/artifacts/ArtifactViewer';
import { EvidenceModal } from './components/sources/EvidenceModal';
import { SettingsModal } from './components/settings/SettingsModal';

export const App: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const [activeCitation, setActiveCitation] = useState<Citation | null>(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorToast, setErrorToast] = useState<string | null>(null);

  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [modelsConfig, setModelsConfig] = useState<ModelsConfig | null>(null);
  const [activeProvider, setActiveProvider] = useState<'local' | 'cloud'>('local');
  const [selectedModel, setSelectedModel] = useState<string>('qwen2.5:0.5b');
  const [availableModels, setAvailableModels] = useState<ModelInfo[]>([]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initial data load
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [healthData, modelsData, sessionsData] = await Promise.all([
        api.getHealth(),
        api.getModels(),
        api.getSessions(),
      ]);

      setHealth(healthData);
      setModelsConfig(modelsData);
      setAvailableModels(modelsData.models || []);
      
      const defaultProv = (modelsData.default_provider || 'local') as 'local' | 'cloud';
      setActiveProvider(defaultProv);
      setSelectedModel(defaultProv === 'local' ? modelsData.active_local_model : modelsData.active_cloud_model);

      setSessions(sessionsData);
      if (sessionsData.length > 0) {
        selectSession(sessionsData[0].id);
      }
    } catch (err: any) {
      console.error('Initialization error:', err);
      showError(err.message || 'Failed connecting to backend.');
    }
  };

  const showError = (msg: string) => {
    setErrorToast(msg);
    setTimeout(() => setErrorToast(null), 5000);
  };

  const selectSession = async (sessionId: string) => {
    setActiveSessionId(sessionId);
    try {
      const sessionDetail = await api.getSession(sessionId);
      setMessages(sessionDetail.messages || []);
      
      // Check if session has artifacts
      const artifacts = await api.getSessionArtifacts(sessionId);
      if (artifacts.length > 0) {
        setActiveArtifact(artifacts[0]);
      } else {
        setActiveArtifact(null);
      }
    } catch (err: any) {
      showError(`Failed loading messages: ${err.message}`);
    }
  };

  const handleNewSession = async () => {
    try {
      const newSession = await api.createSession('New Conversation', activeProvider, selectedModel);
      setSessions([newSession, ...sessions]);
      setActiveSessionId(newSession.id);
      setMessages([]);
      setActiveArtifact(null);
    } catch (err: any) {
      showError(`Failed creating session: ${err.message}`);
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      await api.deleteSession(sessionId);
      const remaining = sessions.filter(s => s.id !== sessionId);
      setSessions(remaining);
      if (activeSessionId === sessionId) {
        if (remaining.length > 0) {
          selectSession(remaining[0].id);
        } else {
          setActiveSessionId(null);
          setMessages([]);
          setActiveArtifact(null);
        }
      }
    } catch (err: any) {
      showError(`Failed deleting session: ${err.message}`);
    }
  };

  const handleSendMessage = async (text: string, requestedSkill?: string) => {
    if (!text.trim() || isLoading) return;

    let targetSessionId = activeSessionId;
    if (!targetSessionId) {
      try {
        const newSession = await api.createSession(
          text.slice(0, 30).trim() || 'New Conversation',
          activeProvider,
          selectedModel
        );
        setSessions([newSession, ...sessions]);
        setActiveSessionId(newSession.id);
        targetSessionId = newSession.id;
      } catch (e: any) {
        showError(`Could not initialize session: ${e.message}`);
        return;
      }
    }

    // Optimistic user message
    const tempUserMsg: Message = {
      id: `temp-${Date.now()}`,
      session_id: targetSessionId,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, tempUserMsg]);
    setIsLoading(true);

    try {
      const response = await api.sendMessage({
        sessionId: targetSessionId,
        message: text,
        provider: activeProvider,
        modelName: selectedModel,
        skill: requestedSkill,
      });

      const assistantMsg: Message = {
        id: response.message_id,
        session_id: response.session_id,
        role: 'assistant',
        content: response.content,
        skill: response.skill,
        citations: response.citations,
        artifact: response.artifact,
        created_at: response.created_at,
      };

      setMessages(prev => [...prev, assistantMsg]);

      // If an artifact was generated, automatically open the side panel!
      if (response.artifact) {
        setActiveArtifact(response.artifact);
      }

      // Refresh sessions list to update titles/timestamps
      const updatedSessions = await api.getSessions();
      setSessions(updatedSessions);

    } catch (err: any) {
      showError(err.message || 'Error executing agent request.');
      // Add error notification inside chat
      const errorMsg: Message = {
        id: `err-${Date.now()}`,
        session_id: targetSessionId,
        role: 'assistant',
        content: `⚠️ **Processing Error**: ${err.message || 'The model provider failed to answer.'}\n\nPlease verify that Ollama or your cloud API credentials are functioning properly in Workspace Settings.`,
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectModel = (modelId: string, provider: 'local' | 'cloud') => {
    setSelectedModel(modelId);
    setActiveProvider(provider);
  };

  const handleTriggerReindex = async () => {
    try {
      await api.triggerIngestion();
      const h = await api.getHealth();
      setHealth(h);
    } catch (e: any) {
      showError(`Re-indexing error: ${e.message}`);
    }
  };

  const currentSession = sessions.find(s => s.id === activeSessionId);

  return (
    <div className="app-container">
      {/* Toast Notification */}
      {errorToast && (
        <div style={{
          position: 'fixed',
          top: '16px',
          right: '16px',
          backgroundColor: '#ef4444',
          color: '#fff',
          padding: '10px 16px',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          zIndex: 9999,
          fontSize: '13px',
          maxWidth: '400px'
        }}>
          <AlertCircle size={16} />
          <span>{errorToast}</span>
        </div>
      )}

      {/* Collapsible Left Sidebar */}
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={selectSession}
        onNewSession={handleNewSession}
        onDeleteSession={handleDeleteSession}
        onOpenSettings={() => setIsSettingsOpen(true)}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        totalIndexedChunks={health?.database.total_indexed_chunks}
      />

      {/* Main Center Workspace */}
      <main className="main-workspace">
        {/* Top Header */}
        <header className="top-header">
          <div className="header-left">
            {isSidebarCollapsed && (
              <button 
                className="toggle-sidebar-btn" 
                onClick={() => setIsSidebarCollapsed(false)}
                title="Open sidebar"
              >
                <Menu size={16} />
              </button>
            )}
            <div className="current-session-title">
              {currentSession ? currentSession.title : 'The Lenny Growth Assistant'}
            </div>
          </div>

          <div className="header-right">
            <ThemeSwitcher />
            <div className="provider-pill" title={`Using ${activeProvider} inference: ${selectedModel}`}>
              <div className="dot" />
              <span>{activeProvider === 'local' ? 'Local Ollama' : 'Cloud LLM'}: {selectedModel}</span>
            </div>
          </div>
        </header>

        {/* Content Area (Split conversation and artifact) */}
        <div className="workspace-content">
          <div className="chat-panel">
            {messages.length === 0 ? (
              <EmptyState onSelectPrompt={handleSendMessage} />
            ) : (
              <div className="chat-messages">
                {messages.map((m) => (
                  <MessageItem
                    key={m.id}
                    message={m}
                    onSelectCitation={(c) => setActiveCitation(c)}
                    onOpenArtifact={(a) => setActiveArtifact(a)}
                  />
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}

            {/* Bottom Composer */}
            <Composer
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              activeProvider={activeProvider}
              selectedModel={selectedModel}
              availableModels={availableModels}
              onSelectModel={handleSelectModel}
            />
          </div>

          {/* Resizable / Toggleable Artifact Workspace Side Panel */}
          {activeArtifact && (
            <ArtifactViewer
              artifact={activeArtifact}
              onClose={() => setActiveArtifact(null)}
            />
          )}
        </div>
      </main>

      {/* Modals */}
      <EvidenceModal
        citation={activeCitation}
        onClose={() => setActiveCitation(null)}
      />

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        health={health}
        modelsConfig={modelsConfig}
        activeProvider={activeProvider}
        onChangeProvider={(p) => {
          setActiveProvider(p);
          if (modelsConfig) {
            setSelectedModel(p === 'local' ? modelsConfig.active_local_model : modelsConfig.active_cloud_model);
          }
        }}
        onTriggerReindex={handleTriggerReindex}
      />
    </div>
  );
};

export default App;
