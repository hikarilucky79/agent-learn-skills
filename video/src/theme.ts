export const PALETTE = {
  bg: "#f5f3ed",
  panel: "#eae8df",
  inputBg: "#e5e0d1",
  ink: "#262821",
  muted: "#696a61",
  border: "#cccbc1",
  accent: "#91412c",
  accentSoft: "#efe4df",
  success: "#2d6a4f",
  successSoft: "#e3efe8",
  codeBg: "#262821",
  codeText: "#f5f3ed",
} as const;

export const FONTS = {
  serif: '"Libre Baskerville", Georgia, "Times New Roman", Times, serif',
  sans: '"Inter", system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
  mono: 'ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace',
} as const;

export type SceneType =
  | "intro"
  | "concept"
  | "code_trace"
  | "active_pause"
  | "quiz_recap";

export interface LessonMeta {
  id: string;
  title: string;
  discipline: string;
  language: "pt-BR" | "en-US";
  voice?: string;
  aspectRatio?: "16:9" | "9:16";
}

export interface ManifestScene {
  index: number;
  type: SceneType;
  heading: string;
  narration: string;
  subtitle?: string;
  body?: string;
  bullets?: string[];
  formula?: string;
  code?: string;
  codeLanguage?: string;
  highlightLines?: number[];
  pauseSeconds?: number;
  answer?: string;
  question?: string;
  options?: string[];
  correctIndex?: number;
  explanation?: string;
  audioPath?: string;
  durationSec: number;
  durationFrames: number;
  pauseFrames: number;
  revealFrames: number;
  totalFrames: number;
}

export interface LessonManifest {
  fps: number;
  totalFrames: number;
  totalDurationSec: number;
  meta: LessonMeta;
  scenes: ManifestScene[];
}
