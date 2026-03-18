import type { DashboardResponse, SessionResponse, UploadResponse, AuthResponse, LoginRequest, SignUpRequest, User, Conversation } from "./types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

let authToken: string | null = null

// Function to set the auth token (called from useAuth hook)
export function setAuthToken(token: string | null) {
  authToken = token
}

export function getAuthToken(): string | null {
  return authToken
}

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>)
  }

  // Add JWT token if available
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`
  }

  const res = await fetch(`${API_BASE}${path}`, {
    headers,
    ...options,
  })

  // Handle 401 - token expired or invalid
  if (res.status === 401) {
    authToken = null
    throw new Error("Unauthorized - please log in again")
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }

  return res.json() as Promise<T>
}

// ─────────────────────────────────────────────────────────────
// Auth API
// ─────────────────────────────────────────────────────────────

export async function login(data: LoginRequest): Promise<AuthResponse> {
  const response = await apiFetch<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  })
  authToken = response.access_token
  return response
}

export async function register(data: SignUpRequest): Promise<AuthResponse> {
  const response = await apiFetch<AuthResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  })
  authToken = response.access_token
  return response
}

export async function refreshToken(refresh_token: string): Promise<AuthResponse> {
  const response = await apiFetch<AuthResponse>("/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token }),
  })
  authToken = response.access_token
  return response
}

export async function getCurrentUser(): Promise<User> {
  return apiFetch<User>("/auth/me")
}

export function logoutApi(): void {
  authToken = null
}

// ─────────────────────────────────────────────────────────────
// Conversation API
// ─────────────────────────────────────────────────────────────

export async function getConversations(): Promise<Conversation[]> {
  return apiFetch<Conversation[]>("/conversations")
}

export async function getConversation(id: string): Promise<Conversation> {
  return apiFetch<Conversation>(`/conversations/${id}`)
}

export async function createConversation(title: string, datasourceId: string = "default"): Promise<Conversation> {
  return apiFetch<Conversation>("/conversations", {
    method: "POST",
    body: JSON.stringify({ title, datasource_id: datasourceId }),
  })
}

export async function deleteConversation(id: string): Promise<void> {
  await apiFetch(`/conversations/${id}`, { method: "DELETE" })
}

export async function addConversationTurn(
  conversationId: string,
  userPrompt: string,
  sqlGenerated?: string,
  charts?: Record<string, unknown>,
  insightSummary?: string,
  dataLimitations?: string,
  executionTimeMs?: number
): Promise<void> {
  await apiFetch(`/conversations/${conversationId}/turns`, {
    method: "POST",
    body: JSON.stringify({
      user_prompt: userPrompt,
      sql_generated: sqlGenerated,
      charts: charts,
      insight_summary: insightSummary,
      data_limitations: dataLimitations,
      execution_time_ms: executionTimeMs,
    }),
  })
}

// ─────────────────────────────────────────────────────────────
// Session & Query API (existing)
// ─────────────────────────────────────────────────────────────

export async function createSession(datasourceId = "default"): Promise<string> {
  const data = await apiFetch<SessionResponse>("/sessions", {
    method: "POST",
    body: JSON.stringify({ datasource_id: datasourceId }),
  });
  return data.session_id;
}

export async function postQuery(
  sessionId: string,
  prompt: string,
  datasourceId = "default"
): Promise<DashboardResponse> {
  return apiFetch<DashboardResponse>("/query", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, prompt, datasource_id: datasourceId }),
  });
}

export async function uploadCsv(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);

  const headers: Record<string, string> = {};
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }

  const res = await fetch(`${API_BASE}/upload/csv`, {
    method: "POST",
    body: form,
    headers
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `HTTP ${res.status}`);
  }
  return res.json() as Promise<UploadResponse>;
}

export async function deleteSession(sessionId: string): Promise<void> {
  await fetch(`${API_BASE}/sessions/${sessionId}`, { method: "DELETE" });
}
