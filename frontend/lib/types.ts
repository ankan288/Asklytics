export interface ChartSpec {
  id: string;
  type: "line" | "bar" | "pie" | "area" | "kpi" | "scatter" | "heatmap" | "histogram";
  title: string;
  data: Record<string, unknown>[];
  x_key?: string;
  y_keys: string[];
  z_key?: string;
  color_palette: string[];
}

export interface ClaimItem {
  claim_text: string;
  claimed_value: string;
  matched_value?: number | null;
  status: "VERIFIED" | "UNVERIFIED" | "CONTRADICTION";
  explanation: string;
}

export interface VerificationResult {
  verified: boolean;
  verification_rate: number;
  claims_total: number;
  claims_verified: number;
  claims: ClaimItem[];
  verified_summary: string;
  badge: string;
}

export interface AuditMetadata {
  sanitized_sql?: string;
  execution_time_ms: number;
  rows_scanned: number;
  is_read_only: boolean;
  confidence_score?: number;
  assumptions?: string[];
  verification?: VerificationResult;
}

export interface DashboardResponse {
  sql?: string;
  dashboard_title: string;
  charts: ChartSpec[];
  insight_summary: string;
  data_limitations?: string;
  follow_up_suggestions?: string[];
  audit?: AuditMetadata;
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
