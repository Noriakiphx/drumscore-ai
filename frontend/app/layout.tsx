import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'DrumScore AI',
  description: 'Audio ⇄ MIDI ⇄ Score JSON ⇄ MusicXML ⇄ PDF/PNG drum score workflow'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
