from __future__ import annotations
from pathlib import Path
from xml.sax.saxutils import escape
from collections import defaultdict
from app.models.score import ScoreJSON

NOTE_MAP = {
    "kick": ("F", 4, 4),
    "snare": ("C", 5, 1),
    "snare_ghost": ("C", 5, 1),
    "cross_stick": ("C", 5, 1),
    "hihat_closed": ("G", 5, 1),
    "hihat_open": ("G", 5, 1),
    "hihat_pedal": ("D", 5, 1),
    "ride": ("F", 5, 1),
    "ride_bell": ("F", 5, 1),
    "crash": ("A", 5, 1),
    "tom_high": ("E", 5, 1),
    "tom_mid": ("B", 4, 1),
    "tom_floor": ("A", 4, 1),
}

def score_to_musicxml(score: ScoreJSON, out_path: str | Path) -> Path:
    divisions = 4  # sixteenth grid per quarter
    events_by_bar = defaultdict(list)
    for ev in score.drum_events:
        events_by_bar[ev.bar].append(ev)

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">',
             '<score-partwise version="3.1">',
             f'<work><work-title>{escape(score.metadata.title)}</work-title></work>',
             '<part-list><score-part id="P1"><part-name>Drumset</part-name></score-part></part-list>',
             '<part id="P1">']
    for bar in score.bars:
        lines.append(f'<measure number="{bar.number}">')
        if bar.number == 1:
            lines.extend([
                '<attributes>', f'<divisions>{divisions}</divisions>', '<key><fifths>0</fifths></key>',
                f'<time><beats>{score.time_signature.numerator}</beats><beat-type>{score.time_signature.denominator}</beat-type></time>',
                '<clef><sign>percussion</sign><line>2</line></clef>', '</attributes>',
                f'<direction placement="above"><direction-type><words>BPM {score.average_bpm:.2f}</words></direction-type></direction>'
            ])
        # section mark
        sec = next((s for s in score.sections if s.start_bar == bar.number), None)
        if sec:
            lines.append(f'<direction placement="above"><direction-type><rehearsal>{escape(sec.name)}</rehearsal></direction-type></direction>')
        # chord symbols as words
        chord_words = [c.symbol for c in score.chords if c.bar == bar.number]
        if chord_words:
            lines.append(f'<direction placement="above"><direction-type><words>{escape("  ".join(chord_words))}</words></direction-type></direction>')

        evs = sorted(events_by_bar.get(bar.number, []), key=lambda e: (e.beat, e.division, e.instrument))
        if not evs:
            lines.append('<note><rest/><duration>16</duration><type>whole</type></note>')
        else:
            for ev in evs:
                step, octave, dur = NOTE_MAP.get(str(ev.instrument), ("C", 5, 1))
                notehead = '<notehead parentheses="yes">normal</notehead>' if ev.articulation == 'ghost' else ''
                accent = '<notations><articulations><accent/></articulations></notations>' if ev.articulation == 'accent' else ''
                lines.append(f'<note><unpitched><display-step>{step}</display-step><display-octave>{octave}</display-octave></unpitched><duration>{dur}</duration><instrument id="P1-I1"/><voice>1</voice><type>16th</type>{notehead}{accent}</note>')
        lines.append('</measure>')
    lines.extend(['</part>', '</score-partwise>'])
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text('\n'.join(lines), encoding='utf-8')
    return out_path
