export interface Citation {
  chunk_id: string;
  doc_title: string;
  doc_url: string;
  speaker?: string;
  date?: string;
  guest?: string;
  excerpt: string;
  score: number;
}

export interface Artifact {
  id: string;
  session_id: string;
  title: string;
  format: 'markdown' | 'html';
  content: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  skill?: string;
  citations?: Citation[];
  artifact?: Artifact | null;
  created_at: string;
}

export interface Session {
  id: string;
  title: string;
  provider: string;
  model_name: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export interface HealthStatus {
  status: string;
  database: {
    connected: boolean;
    total_indexed_chunks: number;
  };
  local_provider: {
    name: string;
    available: boolean;
    message: string;
  };
  cloud_provider: {
    name: string;
    available: boolean;
    message: string;
  };
}

export interface ModelInfo {
  id: string;
  name: string;
  provider: 'local' | 'cloud';
  is_default?: boolean;
}

export interface ModelsConfig {
  default_provider: string;
  active_local_model: string;
  active_cloud_model: string;
  local_status: any;
  cloud_status: any;
  models: ModelInfo[];
}
