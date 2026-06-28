'use client';
import { DrumEvent, ScoreJSON } from '../lib/types';

const lanes: Record<string, number> = {
  crash: 8, ride: 20, ride_bell: 20, hihat_open: 32, hihat_closed: 42, hihat_pedal: 52,
  tom_high: 62, tom_mid: 72, snare: 82, snare_ghost: 82, rimshot: 82, cross_stick: 82,
  tom_floor: 92, kick: 104
};
const symbols: Record<string, string> = {
  kick: '●', snare: '●', snare_ghost: '(●)', rimshot: '◆', cross_stick: 'x',
  hihat_closed: '×', hihat_open: '○', hihat_pedal: '+', ride: '×', ride_bell: '◇',
  crash: '✕', splash: '✕', china: '✕', tom_high: '●', tom_mid: '●', tom_floor: '●'
};

function xPos(event: DrumEvent) {
  const beatOffset = event.beat - 1 + event.division / (event.grid / 4);
  return 4 + (beatOffset / 4) * 92;
}

export function ScoreView({ score, selectedId, onSelect }: { score: ScoreJSON; selectedId?: string | null; onSelect: (event: DrumEvent) => void; }) {
  const sectionName = (id?: string | null) => score.sections.find(s => s.id === id)?.name ?? '';
  return (
    <div className="scorePage">
      <div className="scoreTitle">
        <div><strong>{score.metadata.title}</strong><br/><span>{score.metadata.artist}</span></div>
        <div>BPM {score.average_bpm} / {score.time_signature.numerator}/{score.time_signature.denominator}</div>
      </div>
      <div className="bars">
        {score.bars.map(bar => {
          const events = score.drum_events.filter(e => e.bar === bar.number);
          const chords = score.chords.filter(c => c.bar === bar.number);
          return <div className="bar" key={bar.number}>
            <div className="barHead"><strong>Bar {bar.number}</strong><span className="section">{sectionName(bar.section_id)}</span></div>
            <div className="chords">{chords.map(c => <span key={`${c.bar}-${c.beat}-${c.symbol}`}>{c.symbol}</span>)}</div>
            <div className="staff">
              {[0,1,2,3,4].map(i => <div className="beatLine" key={i} style={{ left: `${4 + i * 23}%` }} />)}
              {events.map((e, i) => <button
                type="button"
                key={e.id ?? `${e.bar}-${e.beat}-${e.division}-${e.instrument}-${i}`}
                className={`note ${e.articulation === 'ghost' || e.instrument === 'snare_ghost' ? 'ghost' : ''} ${(selectedId && selectedId === e.id) ? 'selected' : ''}`}
                style={{ left: `${xPos(e)}%`, top: `${lanes[e.instrument] ?? 82}px` }}
                title={`${e.instrument} bar:${e.bar} beat:${e.beat}.${e.division} vel:${e.velocity}`}
                onClick={() => onSelect(e)}>{symbols[e.instrument] ?? '●'}</button>)}
            </div>
          </div>;
        })}
      </div>
      <div className="legend">
        <span>Kick ●</span><span>Snare ●</span><span>Ghost (●)</span><span>HH closed ×</span><span>HH open ○</span><span>Crash ✕</span><span>Ride ×</span>
      </div>
    </div>
  );
}
