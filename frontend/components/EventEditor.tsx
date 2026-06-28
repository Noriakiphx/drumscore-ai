'use client';
import { DrumEvent, DrumInstrument, ScoreJSON } from '../lib/types';

const instruments: DrumInstrument[] = ['kick','snare','snare_ghost','rimshot','cross_stick','hihat_closed','hihat_open','hihat_pedal','ride','ride_bell','crash','splash','china','tom_high','tom_mid','tom_floor'];
const articulations = ['normal','ghost','accent','flam','drag','choke'] as const;

export function EventEditor({ score, selected, onChange, onDelete, onAdd }: {
  score: ScoreJSON; selected: DrumEvent | null; onChange: (event: DrumEvent) => void; onDelete: (id?: string) => void; onAdd: () => void;
}) {
  const update = (patch: Partial<DrumEvent>) => selected && onChange({ ...selected, ...patch, source: 'human' });
  return <div className="stack">
    <div className="row"><button className="primary" onClick={onAdd}>音符追加</button>{selected && <button className="danger" onClick={() => onDelete(selected.id)}>削除</button>}</div>
    {!selected ? <p className="small">譜面上の音符をクリックして編集します。</p> : <div className="formGrid">
      <label>小節<input type="number" value={selected.bar} min={1} max={score.bars.length} onChange={e => update({ bar: Number(e.target.value) })}/></label>
      <label>拍<input type="number" value={selected.beat} min={1} max={4} step={1} onChange={e => update({ beat: Number(e.target.value) })}/></label>
      <label>Division<input type="number" value={selected.division} min={0} max={7} onChange={e => update({ division: Number(e.target.value) })}/></label>
      <label>Grid<select value={selected.grid} onChange={e => update({ grid: Number(e.target.value) as DrumEvent['grid'] })}>{[4,8,12,16,24,32].map(g => <option key={g}>{g}</option>)}</select></label>
      <label className="full">Instrument<select value={selected.instrument} onChange={e => update({ instrument: e.target.value as DrumInstrument })}>{instruments.map(i => <option key={i}>{i}</option>)}</select></label>
      <label>Velocity<input type="number" value={selected.velocity} min={1} max={127} onChange={e => update({ velocity: Number(e.target.value) })}/></label>
      <label>Articulation<select value={selected.articulation} onChange={e => update({ articulation: e.target.value as DrumEvent['articulation'] })}>{articulations.map(a => <option key={a}>{a}</option>)}</select></label>
    </div>}
  </div>;
}
