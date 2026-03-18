"use client";
import { useState, useEffect } from "react";
import { createSession } from "@/lib/api";

const SESSION_KEY = "bi_session_id";
const DATASOURCE_KEY = "bi_datasource_id";

export function useSession() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [datasourceId, setDatasourceIdState] = useState<string>("default");

  useEffect(() => {
    const stored = localStorage.getItem(SESSION_KEY);
    const storedDs = localStorage.getItem(DATASOURCE_KEY);
    if (storedDs) setDatasourceIdState(storedDs);
    if (stored) {
      setSessionId(stored);
    } else {
      createSession(storedDs || "default").then((id) => {
        setSessionId(id);
        localStorage.setItem(SESSION_KEY, id);
      }).catch(console.error);
    }
  }, []);

  const setDatasourceId = (id: string) => {
    setDatasourceIdState(id);
    localStorage.setItem(DATASOURCE_KEY, id);
    createSession(id).then((newId) => {
      setSessionId(newId);
      localStorage.setItem(SESSION_KEY, newId);
    }).catch(console.error);
  };

  const resetSession = (dsId?: string) => {
    const ds = dsId ?? datasourceId;
    createSession(ds).then((newId) => {
      setSessionId(newId);
      localStorage.setItem(SESSION_KEY, newId);
    }).catch(console.error);
  };

  return { sessionId, datasourceId, setDatasourceId, resetSession };
}
