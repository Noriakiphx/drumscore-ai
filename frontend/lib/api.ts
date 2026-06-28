import { ScoreJSON } from './types';

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';

export async function uploadAudio(file: File) {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${API_BASE}/v1/jobs`, { method: 'POST', body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getJob(jobId: string) {
  const res = await fetch(`${API_BASE}/v1/jobs/${jobId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getScore(jobId: string): Promise<ScoreJSON> {
  const res = await fetch(`${API_BASE}/v1/jobs/${jobId}/score`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function validateScore(score: ScoreJSON) {
  const res = await fetch(`${API_BASE}/v1/validate/score`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(score)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function downloadFromPost(path: string, score: ScoreJSON, filename: string) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(score)
  });
  if (!res.ok) throw new Error(await res.text());
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export function exportMidi(score: ScoreJSON) { return downloadFromPost('/v1/convert/score-to-midi', score, 'drumscore.mid'); }
export function exportMusicXml(score: ScoreJSON) { return downloadFromPost('/v1/convert/score-to-musicxml', score, 'drumscore.musicxml'); }
