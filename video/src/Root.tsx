import React from "react";
import {
  AbsoluteFill,
  Audio,
  Composition,
  Series,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { FONTS, LessonManifest, ManifestScene, PALETTE } from "./theme";
import { IntroScene } from "./scenes/IntroScene";
import { ConceptScene } from "./scenes/ConceptScene";
import { CodeTraceScene } from "./scenes/CodeTraceScene";
import { ActivePauseScene } from "./scenes/ActivePauseScene";
import { QuizRecapScene } from "./scenes/QuizRecapScene";

export type LessonVideoProps = {
  manifest: LessonManifest;
};

const DEFAULT_MANIFEST: LessonManifest = {
  fps: 30,
  totalFrames: 300,
  totalDurationSec: 10,
  meta: {
    id: "preview-lesson",
    title: "Editorial Notebook Preview",
    discipline: "Software Engineering",
    language: "en-US",
    aspectRatio: "16:9",
  },
  scenes: [
    {
      index: 0,
      type: "intro",
      heading: "Programmatic Video Lessons",
      subtitle: "Editorial Notebook design + deterministic TTS timing",
      narration: "Welcome to agent video lessons.",
      durationSec: 5,
      durationFrames: 150,
      pauseFrames: 0,
      revealFrames: 0,
      totalFrames: 150,
    },
    {
      index: 1,
      type: "active_pause",
      heading: "Quick Check",
      body: "Why separate script generation (lesson.json) from video rendering?",
      pauseSeconds: 4,
      answer: "Deterministic rendering keeps code crisp, timings exact, and captions synchronized.",
      narration: "Take a moment to think.",
      durationSec: 1,
      durationFrames: 30,
      pauseFrames: 120,
      revealFrames: 0,
      totalFrames: 150,
    },
  ],
};

const renderSceneContent = (
  scene: ManifestScene,
  manifest: LessonManifest,
  sceneNumber: number
): React.ReactNode => {
  switch (scene.type) {
    case "intro":
      return <IntroScene scene={scene} meta={manifest.meta} />;
    case "concept":
      return <ConceptScene scene={scene} sceneNumber={sceneNumber} />;
    case "code_trace":
      return <CodeTraceScene scene={scene} sceneNumber={sceneNumber} />;
    case "active_pause":
      return (
        <ActivePauseScene
          scene={scene}
          meta={manifest.meta}
          sceneNumber={sceneNumber}
        />
      );
    case "quiz_recap":
      return (
        <QuizRecapScene
          scene={scene}
          meta={manifest.meta}
          sceneNumber={sceneNumber}
        />
      );
    default:
      return <ConceptScene scene={scene} sceneNumber={sceneNumber} />;
  }
};

export const LessonComposition: React.FC<LessonVideoProps> = ({ manifest }) => {
  const frame = useCurrentFrame();
  const { durationInFrames, width, height } = useVideoConfig();
  const isVertical = height > width;
  const progressPct = Math.min(100, (frame / Math.max(1, durationInFrames - 1)) * 100);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: PALETTE.bg,
        color: PALETTE.ink,
        fontFamily: FONTS.sans,
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Editorial Top Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: isVertical ? "28px 44px 16px" : "24px 64px 14px",
          borderBottom: `1.5px solid ${PALETTE.border}`,
          fontFamily: FONTS.mono,
          fontSize: isVertical ? 18 : 16,
          color: PALETTE.muted,
          letterSpacing: "0.06em",
          textTransform: "uppercase",
        }}
      >
        <span style={{ color: PALETTE.ink, fontWeight: 700 }}>
          {manifest.meta.discipline}
        </span>
        <span
          style={{
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
            maxWidth: isVertical ? 460 : 960,
          }}
        >
          {manifest.meta.title}
        </span>
      </div>

      {/* Main Scene Sequence */}
      <div style={{ flex: 1, display: "flex", position: "relative" }}>
        <Series>
          {manifest.scenes.map((scene, idx) => (
            <Series.Sequence
              key={`${scene.type}-${idx}`}
              durationInFrames={Math.max(1, scene.totalFrames)}
            >
              <AbsoluteFill style={{ display: "flex", flexDirection: "column" }}>
                {scene.audioPath ? (
                  <Audio src={staticFile(scene.audioPath)} />
                ) : null}
                {renderSceneContent(scene, manifest, idx + 1)}
              </AbsoluteFill>
            </Series.Sequence>
          ))}
        </Series>
      </div>

      {/* Bottom Progress Bar */}
      <div
        style={{
          height: 8,
          width: "100%",
          backgroundColor: PALETTE.panel,
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${progressPct}%`,
            backgroundColor: PALETTE.accent,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="LessonVideo"
      component={LessonComposition}
      durationInFrames={DEFAULT_MANIFEST.totalFrames}
      fps={DEFAULT_MANIFEST.fps}
      width={1920}
      height={1080}
      defaultProps={{ manifest: DEFAULT_MANIFEST }}
      calculateMetadata={({ props }: { props: LessonVideoProps }) => {
        const manifest = props.manifest ?? DEFAULT_MANIFEST;
        const isVertical = manifest.meta.aspectRatio === "9:16";
        const totalFrames = manifest.scenes.reduce(
          (sum: number, scene: ManifestScene) => sum + Math.max(1, scene.totalFrames),
          0
        );
        return {
          fps: manifest.fps || 30,
          durationInFrames: Math.max(1, totalFrames),
          width: isVertical ? 1080 : 1920,
          height: isVertical ? 1920 : 1080,
        };
      }}
    />
  );
};
