"use client";

import { useState } from "react";
import { API_BASE } from "../../lib/api";

type TempoPoint = {
  time_sec: number;
  bpm: number;
};

type TempoCandidate = {
  bpm: number;
  score: number;
  alignment?: number;
  stability?: number;
  strong_beat_ratio?: number;
};

type Fingerprint = {
  original_filename?: string;
  duration_sec: number;
  sample_rate: number;
  estimated_bpm: number;
  raw_bpm?: number;
  tempo_confidence?: number;
  tempo_candidates?: TempoCandidate[];
  tempo_map?: TempoPoint[];
  beat_count: number;
  transient_count: number;
  rms_energy_mean: number;
  rms_energy_max: number;
  dynamic_range: number;
  spectral_centroid_mean: number;
  zero_crossing_rate_mean: number;
  spectral_flux_mean: number;
  performance_fingerprint_v0_1?: {
    energy_flow?: number;
    groove_vector?: number[];
    status?: string;
  };
};

function TempoMapChart({ points }: { points: TempoPoint[] }) {
  if (!points.length) {
    return <p style={{ color: "#8fa0b5" }}>Tempo map is not available.</p>;
  }

  const width = 900;
  const height = 240;
  const padding = 28;
  const bpms = points.map((point) => point.bpm);
  const minBpm = Math.min(...bpms);
  const maxBpm = Math.max(...bpms);
  const span = Math.max(1, maxBpm - minBpm);
  const maxTime = Math.max(1, points[points.length - 1].time_sec);

  const polyline = points
    .map((point) => {
      const x = padding + (point.time_sec / maxTime) * (width - padding * 2);
      const y =
        height -
        padding -
        ((point.bpm - minBpm) / span) * (height - padding * 2);
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div style={{ overflowX: "auto" }}>
      <svg viewBox={`0 0 ${width} ${height}`} style={{ width: "100%", minWidth: 620 }}>
        <rect x="0" y="0" width={width} height={height} rx="14" fill="#0f141b" />
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#334155" />
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="#334155" />
        <polyline points={polyline} fill="none" stroke="#49B6FF" strokeWidth="4" />
        {points.map((point, index) => {
          const [x, y] = polyline.split(" ")[index].split(",").map(Number);
          return <circle key={`${point.time_sec}-${index}`} cx={x} cy={y} r="4" fill="#7B4DFF" />;
        })}
        <text x={padding} y={18} fill="#8fa0b5" fontSize="13">
          {maxBpm.toFixed(2)} BPM
        </text>
        <text x={padding} y={height - 6} fill="#8fa0b5" fontSize="13">
          {minBpm.toFixed(2)} BPM
        </text>
      </svg>
    </div>
  );
}

function Bar({
  label,
  value,
  maximum,
}: {
  label: string;
  value: number;
  maximum: number;
}) {
  const percentage = Math.max(0, Math.min(100, (value / maximum) * 100));

  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 7 }}>
        <span style={{ color: "#aab4c3" }}>{label}</span>
        <strong>{value}</strong>
      </div>
      <div style={{ height: 11, borderRadius: 999, background: "#273142" }}>
        <div
          style={{
            width: `${percentage}%`,
            height: "100%",
            borderRadius: 999,
            background: "linear-gradient(90deg,#49B6FF,#7B4DFF)",
          }}
        />
      </div>
    </div>
  );
}

export default function PerformanceFingerprintPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<Fingerprint | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyze() {
    if (!file) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const form = new FormData();
      form.append("file", file);

      const response = await fetch(`${API_BASE}/v1/performance-fingerprint`, {
        method: "POST",
        body: form,
      });

      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail || "Analysis failed");
      }

      setResult(payload);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  const groove = result?.performance_fingerprint_v0_1?.groove_vector ?? [];
  const tempoMap = result?.tempo_map ?? [];
  const candidates = result?.tempo_candidates ?? [];

  return (
    <main style={{ minHeight: "100vh", padding: 40, background: "#0b0f14" }}>
      <div style={{ maxWidth: 1180, margin: "0 auto" }}>
        <a href="/" style={{ color: "#49B6FF" }}>
          ← Home
        </a>

        <h1 style={{ fontSize: 46 }}>Performance Fingerprint v0.3</h1>
        <p style={{ color: "#aab4c3" }}>
          Advanced tempo selection, Tempo Map, and prototype groove visualization.
        </p>

        <section
          style={{
            marginTop: 28,
            padding: 24,
            borderRadius: 18,
            background: "#151b23",
            border: "1px solid #273142",
          }}
        >
          <input
            type="file"
            accept="audio/*"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
          <button
            onClick={analyze}
            disabled={!file || loading}
            style={{
              marginLeft: 12,
              padding: "10px 18px",
              borderRadius: 10,
              border: 0,
              cursor: "pointer",
            }}
          >
            {loading ? "Analyzing..." : "Analyze"}
          </button>

          {error && <p style={{ color: "#ff7a7a" }}>{error}</p>}
        </section>

        {result && (
          <>
            <section
              style={{
                marginTop: 24,
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
                gap: 18,
              }}
            >
              {[
                ["Selected BPM", result.estimated_bpm],
                ["Raw BPM", result.raw_bpm ?? "-"],
                ["Confidence", result.tempo_confidence ?? "-"],
                ["Duration", `${result.duration_sec} sec`],
                ["Beat Count", result.beat_count],
                ["Transient Count", result.transient_count],
                ["RMS Mean", result.rms_energy_mean],
                ["Dynamic Range", result.dynamic_range],
                ["Spectral Centroid", `${result.spectral_centroid_mean} Hz`],
              ].map(([label, value]) => (
                <div
                  key={String(label)}
                  style={{
                    background: "#151b23",
                    border: "1px solid #273142",
                    borderRadius: 16,
                    padding: 20,
                  }}
                >
                  <div style={{ color: "#8fa0b5", fontSize: 14 }}>{label}</div>
                  <div style={{ fontSize: 26, fontWeight: 700, marginTop: 8 }}>
                    {value}
                  </div>
                </div>
              ))}
            </section>

            <section
              style={{
                marginTop: 24,
                background: "#151b23",
                border: "1px solid #273142",
                borderRadius: 18,
                padding: 24,
              }}
            >
              <h2>Tempo Map</h2>
              <TempoMapChart points={tempoMap} />
            </section>

            <section
              style={{
                marginTop: 24,
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 18,
              }}
            >
              <div
                style={{
                  background: "#151b23",
                  border: "1px solid #273142",
                  borderRadius: 18,
                  padding: 24,
                }}
              >
                <h2>Tempo Candidates</h2>
                {candidates.length ? (
                  candidates.slice(0, 6).map((candidate) => (
                    <Bar
                      key={`${candidate.bpm}-${candidate.score}`}
                      label={`${candidate.bpm} BPM`}
                      value={candidate.score}
                      maximum={1}
                    />
                  ))
                ) : (
                  <p style={{ color: "#8fa0b5" }}>No candidates.</p>
                )}
              </div>

              <div
                style={{
                  background: "#151b23",
                  border: "1px solid #273142",
                  borderRadius: 18,
                  padding: 24,
                }}
              >
                <h2>Groove Vector v0.1</h2>
                {groove.length ? (
                  groove.map((value, index) => (
                    <Bar
                      key={`${value}-${index}`}
                      label={`Axis ${index + 1}`}
                      value={Math.abs(value)}
                      maximum={Math.max(...groove.map((item) => Math.abs(item)), 1)}
                    />
                  ))
                ) : (
                  <p style={{ color: "#8fa0b5" }}>No groove vector.</p>
                )}
              </div>
            </section>
          </>
        )}
      </div>
    </main>
  );
}
