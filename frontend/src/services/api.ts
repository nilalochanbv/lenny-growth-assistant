import type { Session, Message, Artifact, HealthStatus, ModelsConfig } from '../types';

const API_BASE = '/api/v1';

export const api = {
  async getHealth(): Promise<HealthStatus> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
    return res.json();
  },

  async getModels(): Promise<ModelsConfig> {
    const res = await fetch(`${API_BASE}/models`);
    if (!res.ok) throw new Error(`Failed to load models: ${res.statusText}`);
    return res.json();
  },

  async getSessions(): Promise<Session[]> {
    const res = await fetch(`${API_BASE}/sessions`);
    if (!res.ok) throw new Error(`Failed to load sessions: ${res.statusText}`);
    return res.json();
  },

  async getSession(sessionId: string): Promise<Session & { messages: Message[] }> {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
    if (!res.ok) throw new Error(`Failed to load session details: ${res.statusText}`);
    return res.json();
  },

  async createSession(title: string = 'New Conversation', provider: string = 'local', modelName?: string): Promise<Session> {
    const res = await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, provider, model_name: modelName }),
    });
    if (!res.ok) throw new Error(`Failed to create session: ${res.statusText}`);
    return res.json();
  },

  async deleteSession(sessionId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error(`Failed to delete session: ${res.statusText}`);
  },

  async sendMessage(params: {
    sessionId?: string;
    message: string;
    provider?: string;
    modelName?: string;
    skill?: string;
  }): Promise<{
    session_id: string;
    message_id: string;
    role: string;
    content: string;
    skill: string;
    provider_used: string;
    model_used: string;
    citations: any[];
    artifact: Artifact | null;
    created_at: string;
  }> {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: params.sessionId,
        message: params.message,
        provider: params.provider,
        model_name: params.modelName,
        skill: params.skill,
      }),
    });
    if (!res.ok) {
      let errDetail = 'Chat request failed';
      try {
        const errorData = await res.json();
        errDetail = errorData.detail || errorData.error?.message || errDetail;
      } catch (e) {
        errDetail = res.statusText;
      }
      throw new Error(errDetail);
    }
    return res.json();
  },

  async getArtifact(artifactId: string): Promise<Artifact> {
    const res = await fetch(`${API_BASE}/artifacts/${artifactId}`);
    if (!res.ok) throw new Error(`Failed to fetch artifact: ${res.statusText}`);
    return res.json();
  },

  async getSessionArtifacts(sessionId: string): Promise<Artifact[]> {
    const res = await fetch(`${API_BASE}/artifacts/session/${sessionId}`);
    if (!res.ok) throw new Error(`Failed to fetch session artifacts: ${res.statusText}`);
    return res.json();
  },

  async triggerIngestion(): Promise<any> {
    const res = await fetch(`${API_BASE}/ingestion/run`, { method: 'POST' });
    return res.json();
  },

  async getIngestionStatus(): Promise<{ total_chunks: number; distinct_documents: number; is_indexed: boolean }> {
    const res = await fetch(`${API_BASE}/ingestion/status`);
    return res.json();
  }
};
