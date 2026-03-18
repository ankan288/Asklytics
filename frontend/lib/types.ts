export interface ChartSpec {
  id: string;
  type: "line" | "bar" | "pie" | "area" | "kpi";
  title: string;
  data: Record<string, unknown>[];
  x_key?: string;
  y_keys: string[];
  color_palette: string[];
}

export interface DashboardResponse {
  sql?: string;
  dashboard_title: string;
  charts: ChartSpec[];
  insight_summary: string;
  data_limitations?: string;
  follow_up_suggestions?: string[];
  error?: string;
}

export interface SessionResponse {
  session_id: string;
}

export interface UploadResponse {
  datasource_id: string;
  table_name: string;
  columns: Record<string, string>;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  warning?: string;
  timestamp: Date;
}

// Auth types
export interface User {
  id: string;
  email: string;
  display_name?: string;
  avatar_url?: string;
  created_at?: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignUpRequest {
  email: string;
  password: string;
  display_name?: string;
}

// Conversation history types
export interface ConversationTurn {
  id: string;
  turn_number: number;
  user_prompt: string;
  sql_generated?: string;
  charts?: Record<string, unknown>;
  insight_summary?: string;
  data_limitations?: string;
  execution_time_ms?: number;
  created_at: string;
}

export interface Conversation {
  id: string;
  title?: string;
  datasource_id: string;
  created_at: string;
  updated_at: string;
  turns?: ConversationTurn[];
  turn_count?: number;
}
