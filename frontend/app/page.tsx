'use client';
import { useMemo, useState } from 'react';
import { EventEditor } from '../components/EventEditor';
import { ScoreView } from '../components/ScoreView';
import { exportMidi, exportMusicXml, getJob, getScore, uploadAudio, validateScore } from '../lib/api';
import { sampleScore } from '../lib/sampleScore';
import { DrumEvent, ScoreJSON } from '../lib/types';

function clone<T>(v: T): T { return JSON.parse(JSON.stringify(v)); }

export default function Home() {
  const [score, setScore] = useState<ScoreJSON>(clone(sampleScore));
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string>('');
  const [status, setStatus] = useState<string>('sample loaded');
  const [jsonText, setJsonText] = useState<string>(JSON.stringify(sampleScore, null, 2));

  const selected = useMemo(() => score.drum_events.find(e => e.id === selectedId) ?? null, [score, selectedId]);
  const sectionCount = score.sections.length;
  const ghostCount = score.drum_events.filter(e => e.articulation === 'ghost' || e.instrument === 'snare_ghost').length;

  function sync(next: ScoreJSON) { setScore(next); setJsonText(JSON.stringify(next, null, 2)); }
  function updateEvent(event: DrumEvent) {
    const next = clone(score);
    next.drum_events = next.drum_events.map(e => e.id === event.id ? event : e);
    sync(next);
  }
  function addEvent() {
    const id = `human-${Date.now()}`;
    const event: DrumEvent = { id, time_sec: 0, bar: 1, beat: 1, division: 0, grid: 16, instrument: 'kick', velocity: 96, articulation: 'normal', duration_sec: .05, confidence: 1, source: 'human' };
    sync({ ...score, drum_events: [...score.drum_events, event] });
    setSelectedId(id);
  }
  function deleteEvent(id?: string) {
    if (!id) return;
    sync({ ...score, drum_events: score.drum_events.filter(e => e.id !== id) });
    setSelectedId(null);
  }
  async function handleUpload(file?: File) {
    if (!file) return;
    setStatus('uploading...');
    const job = await uploadAudio(file);
    setJobId(job.job_id);
    setStatus(`job created: ${job.job_id}`);
  }
  async function refreshJob() {
    if (!jobId) return;
    const job = await getJob(jobId);
    setStatus(JSON.stringify(job));
    if (job.status === 'done' || job.status === 'completed') {
      const s = await getScore(jobId);
      sync(s);
      setStatus('score loaded from API');
    }
  }
  async function validate() {
    const result = await validateScore(score);
    setStatus(`valid: ${result.valid}, events: ${result.events}, bars: ${result.bars}`);
  }
  function importJson() {
    try { sync(JSON.parse(jsonText)); setStatus('JSON imported'); } catch (e) { setStatus(`JSON error: ${String(e)}`); }
  }

  return <main className="container">
    <div className="header">
      <div><h1 className="title">DrumScore AI GUI</h1><p className="subtitle">Audio ⇄ MIDI ⇄ Score JSON ⇄ MusicXML ⇄ PDF/PNG の往復編集プロトタイプ</p></div>
      <div className="row"><button onClick={() => exportMidi(score)}>MIDI出力</button><button onClick={() => exportMusicXml(score)}>MusicXML出力</button><button className="primary" onClick={validate}>Validate</button></div>
    </div>
    <div className="grid">
      <aside className="panel stack">
        <h2>Project</h2>
        <input type="file" accept="audio/*,.mid,.midi" onChange={e => handleUpload(e.target.files?.[0])}/>
        <div className="row"><input placeholder="job id" value={jobId} onChange={e => setJobId(e.target.value)} /><button onClick={refreshJob}>取得</button></div>
        <p className="small">{status}</p>
        <div className="kpi"><div><span className="small">Bars</span><strong>{score.bars.length}</strong></div><div><span className="small">Events</span><strong>{score.drum_events.length}</strong></div><div><span className="small">Ghost</span><strong>{ghostCount}</strong></div><div><span className="small">Sections</span><strong>{sectionCount}</strong></div></div>
        <h2>Event Editor</h2>
        <EventEditor score={score} selected={selected} onChange={updateEvent} onDelete={deleteEvent} onAdd={addEvent}/>
        <h2>Score JSON</h2>
        <textarea value={jsonText} onChange={e => setJsonText(e.target.value)} />
        <button onClick={importJson}>JSONを譜面へ反映</button>
      </aside>
      <section className="panel">
        <div className="scoreToolbar"><h2>Score View</h2><span className="small">クリックで音符編集 / ゴーストノート対応</span></div>
        <ScoreView score={score} selectedId={selectedId} onSelect={(e) => setSelectedId(e.id ?? null)} />
      </section>
    </div>
  </main>;
}
