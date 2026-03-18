"use client";
import { useState, useRef } from "react";
import { Upload, X, FileText, CheckCircle } from "lucide-react";
import { LoadingSpinner } from "./LoadingSpinner";
import { uploadCsv } from "@/lib/api";
import type { UploadResponse } from "@/lib/types";

interface Props {
  onClose: () => void;
  onUpload: (result: UploadResponse) => void;
}

export function FileUploadModal({ onClose, onUpload }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (f: File) => {
    if (!f.name.endsWith(".csv")) {
      setError("Only .csv files are supported.");
      return;
    }
    setFile(f);
    setError(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const result = await uploadCsv(file);
      onUpload(result);
      onClose();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Upload failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 w-full max-w-md shadow-2xl mx-4">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-white font-semibold text-lg">Upload Your Dataset</h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
            dragging
              ? "border-indigo-500 bg-indigo-950/30"
              : "border-slate-600 hover:border-indigo-500 hover:bg-slate-800/50"
          }`}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
          />
          {file ? (
            <div className="flex items-center justify-center gap-2 text-indigo-400">
              <CheckCircle size={20} />
              <span className="font-medium">{file.name}</span>
              <span className="text-slate-500 text-xs">
                ({(file.size / 1024).toFixed(0)} KB)
              </span>
            </div>
          ) : (
            <>
              <Upload className="mx-auto mb-3 text-slate-500" size={32} />
              <p className="text-slate-300 font-medium text-sm">
                Drag & drop a CSV file here
              </p>
              <p className="text-slate-500 text-xs mt-1">or click to browse</p>
            </>
          )}
        </div>

        {error && (
          <p className="text-red-400 text-sm mt-3 flex items-center gap-1.5">
            <X size={14} /> {error}
          </p>
        )}

        <button
          onClick={handleSubmit}
          disabled={!file || loading}
          className="mt-5 w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2.5 rounded-xl transition-colors"
        >
          {loading ? (
            <><LoadingSpinner size={16} /> Processing...</>
          ) : (
            <><FileText size={16} /> Upload & Query This Dataset</>
          )}
        </button>

        <p className="text-slate-600 text-xs text-center mt-3">
          Max 50 MB. The file is loaded into a private in-memory database.
        </p>
      </div>
    </div>
  );
}
