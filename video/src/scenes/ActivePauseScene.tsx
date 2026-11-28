import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { FONTS, LessonMeta, ManifestScene, PALETTE } from "../theme";

interface ActivePauseSceneProps {
  scene: ManifestScene;
  meta: LessonMeta;
  sceneNumber: number;
}

export const ActivePauseScene: React.FC<ActivePauseSceneProps> = ({
  scene,
  meta,
  sceneNumber,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const isVertical = height > width;
  const isPt = meta.language === "pt-BR";

  const speechEnd = scene.durationFrames;
  const pauseEnd = speechEnd + scene.pauseFrames;
  const inPausePhase = frame >= speechEnd && frame < pauseEnd;
  const inRevealPhase = frame >= pauseEnd && scene.revealFrames > 0;

  const pauseProgress =
    scene.pauseFrames > 0
      ? interpolate(frame, [speechEnd, pauseEnd], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })
      : 1;

  const secondsLeft = Math.max(
    0,
    Math.ceil((pauseEnd - Math.max(frame, speechEnd)) / fps)
  );

  const revealSpring = spring({
    frame: Math.max(0, frame - pauseEnd),
    fps,
    config: { damping: 18, stiffness: 120 },
  });

  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        padding: isVertical ? "48px 50px" : "48px 96px",
        gap: 26,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 12,
        }}
      >
        <div
          style={{
            fontFamily: FONTS.mono,
            fontSize: 18,
            fontWeight: 600,
            letterSpacing: "0.09em",
            textTransform: "uppercase",
            color: PALETTE.accent,
          }}
        >
          {String(sceneNumber).padStart(2, "0")} / ACTIVE PAUSE
        </div>

        <div
          style={{
            backgroundColor: inRevealPhase ? PALETTE.successSoft : PALETTE.accentSoft,
            color: inRevealPhase ? PALETTE.success : PALETTE.accent,
            border: `1.5px solid ${inRevealPhase ? PALETTE.success : PALETTE.accent}`,
            borderRadius: 999,
            padding: "8px 20px",
            fontFamily: FONTS.mono,
            fontSize: 20,
            fontWeight: 700,
          }}
        >
          {inRevealPhase
            ? isPt
              ? "RESPOSTA"
              : "ANSWER"
            : inPausePhase
              ? isPt
                ? `PENSE AGORA • ${secondsLeft}s`
                : `THINK NOW • ${secondsLeft}s`
              : isPt
                ? "PREPARE SUA PREVISÃO"
                : "PREPARE YOUR PREDICTION"}
        </div>
      </div>

      <h2
        style={{
          margin: 0,
          fontFamily: FONTS.serif,
          fontSize: isVertical ? 46 : 52,
          lineHeight: 1.2,
          color: PALETTE.ink,
        }}
      >
        {scene.heading}
      </h2>

      <div
        style={{
          backgroundColor: PALETTE.panel,
          border: `2px solid ${PALETTE.ink}`,
          borderRadius: 12,
          padding: isVertical ? "28px 28px" : "30px 36px",
          fontFamily: FONTS.sans,
          fontSize: isVertical ? 30 : 32,
          lineHeight: 1.45,
          color: PALETTE.ink,
        }}
      >
        {scene.body ?? scene.question ?? scene.narration}
      </div>

      {/* Countdown bar */}
      <div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            fontFamily: FONTS.mono,
            fontSize: 18,
            color: PALETTE.muted,
            marginBottom: 8,
          }}
        >
          <span>
            {isPt ? "Contagem regressiva de aprendizagem ativa" : "Active recall countdown"}
          </span>
          <span>{scene.pauseSeconds ?? Math.round(scene.pauseFrames / fps)}s</span>
        </div>
        <div
          style={{
            width: "100%",
            height: 16,
            backgroundColor: PALETTE.inputBg,
            borderRadius: 999,
            overflow: "hidden",
            border: `1px solid ${PALETTE.border}`,
          }}
        >
          <div
            style={{
              width: `${Math.max(0, (1 - pauseProgress) * 100)}%`,
              height: "100%",
              backgroundColor: inRevealPhase ? PALETTE.success : PALETTE.accent,
              borderRadius: 999,
            }}
          />
        </div>
      </div>

      {scene.answer ? (
        <div
          style={{
            opacity: inRevealPhase ? revealSpring : 0.14,
            transform: `translateY(${inRevealPhase ? interpolate(revealSpring, [0, 1], [16, 0]) : 8}px)`,
            backgroundColor: PALETTE.successSoft,
            border: `2px solid ${PALETTE.success}`,
            borderRadius: 12,
            padding: isVertical ? "24px 28px" : "24px 32px",
            fontFamily: FONTS.sans,
            fontSize: isVertical ? 27 : 28,
            lineHeight: 1.45,
            color: PALETTE.ink,
          }}
        >
          <div
            style={{
              fontFamily: FONTS.mono,
              fontSize: 17,
              fontWeight: 700,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              color: PALETTE.success,
              marginBottom: 8,
            }}
          >
            {inRevealPhase
              ? isPt
                ? "Resposta revelada"
                : "Revealed Answer"
              : isPt
                ? "Resposta oculta até o fim da contagem"
                : "Answer hidden until countdown finishes"}
          </div>
          {inRevealPhase ? scene.answer : "••••••••••••••••••••••••••••••••••••••••"}
        </div>
      ) : null}
    </div>
  );
};
