export type DrumInstrument =
  | 'kick' | 'snare' | 'snare_ghost' | 'rimshot' | 'cross_stick'
  | 'hihat_closed' | 'hihat_open' | 'hihat_pedal'
  | 'ride' | 'ride_bell' | 'crash' | 'splash' | 'china'
  | 'tom_high' | 'tom_mid' | 'tom_floor';

export type Articulation = 'normal' | 'ghost' | 'accent' | 'flam' | 'drag' | 'choke';

export type DrumEvent = {
  id?: string;
  time_sec: number;
  bar: number;
  beat: number;
  division: number;
  grid: 4 | 8 | 12 | 16 | 24 | 32;
  instrument: DrumInstrument;
  velocity: number;
  articulation: Articulation;
  duration_sec: number;
  confidence: number;
  source: 'ai' | 'human' | 'imported';
};

export type ScoreJSON = {
  metadata: { title: string; artist?: string | null; source_audio?: string | null; created_by: string; schema_version: string; };
  average_bpm: number;
  time_signature: { numerator: number; denominator: number; };
  ticks_per_quarter: number;
  tempo_map: Array<{ time_sec: number; beat_index: number; bpm: number; confidence: number; }>;
  sections: Array<{ id: string; name: string; start_bar: number; end_bar: number; }>;
  bars: Array<{ number: number; start_sec: number; end_sec: number; section_id?: string | null; rehearsal_mark?: string | null; }>;
  chords: Array<{ bar: number; beat: number; symbol: string; confidence: number; }>;
  drum_events: DrumEvent[];
};
