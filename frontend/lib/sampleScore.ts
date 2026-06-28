import { ScoreJSON } from './types';

const bpm = 82;
const beatSec = 60 / bpm;
const bars = Array.from({ length: 10 }, (_, i) => ({
  number: i + 1,
  start_sec: i * beatSec * 4,
  end_sec: (i + 1) * beatSec * 4,
  section_id: i < 2 ? 'intro' : i < 6 ? 'verse' : 'chorus',
  rehearsal_mark: null
}));
const ev = (bar: number, beat: number, division: number, instrument: any, velocity = 90, articulation: any = 'normal') => ({
  id: `${bar}-${beat}-${division}-${instrument}-${Math.random().toString(16).slice(2, 8)}`,
  time_sec: ((bar - 1) * 4 + (beat - 1) + division / 4) * beatSec,
  bar, beat, division, grid: 16 as const, instrument, velocity, articulation,
  duration_sec: 0.05, confidence: 1, source: 'human' as const
});

export const sampleScore: ScoreJSON = {
  metadata: { title: '30sec Ghost Note Groove', artist: 'DrumScore AI', source_audio: null, created_by: 'DrumScore AI', schema_version: '1.0.0' },
  average_bpm: bpm,
  time_signature: { numerator: 4, denominator: 4 },
  ticks_per_quarter: 480,
  tempo_map: Array.from({ length: 41 }, (_, i) => ({ time_sec: i * beatSec, beat_index: i, bpm, confidence: 1 })),
  sections: [
    { id: 'intro', name: 'Intro', start_bar: 1, end_bar: 2 },
    { id: 'verse', name: 'Verse A', start_bar: 3, end_bar: 6 },
    { id: 'chorus', name: 'Chorus', start_bar: 7, end_bar: 10 }
  ],
  bars,
  chords: [
    { bar: 1, beat: 1, symbol: 'Am7', confidence: .6 }, { bar: 2, beat: 1, symbol: 'D7', confidence: .6 },
    { bar: 3, beat: 1, symbol: 'Gmaj7', confidence: .6 }, { bar: 4, beat: 1, symbol: 'Em7', confidence: .6 },
    { bar: 5, beat: 1, symbol: 'Am7', confidence: .6 }, { bar: 6, beat: 1, symbol: 'D7', confidence: .6 },
    { bar: 7, beat: 1, symbol: 'G', confidence: .6 }, { bar: 8, beat: 1, symbol: 'Bm7', confidence: .6 },
    { bar: 9, beat: 1, symbol: 'C', confidence: .6 }, { bar: 10, beat: 1, symbol: 'D7', confidence: .6 }
  ],
  drum_events: bars.flatMap(b => {
    const bar = b.number;
    return [
      ev(bar, 1, 0, 'kick', 112), ev(bar, 3, 0, 'kick', 108),
      ev(bar, 2, 0, 'snare', 108), ev(bar, 4, 0, 'snare', 110),
      ev(bar, 1, 2, 'snare_ghost', 38, 'ghost'), ev(bar, 2, 3, 'snare_ghost', 34, 'ghost'), ev(bar, 3, 2, 'snare_ghost', 42, 'ghost'),
      ...[1,2,3,4].flatMap(beat => [0,2].map(div => ev(bar, beat, div, bar >= 7 && beat === 1 && div === 0 ? 'hihat_open' : 'hihat_closed', 72)))
    ];
  })
};
