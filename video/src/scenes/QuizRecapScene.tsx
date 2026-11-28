import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { FONTS, LessonMeta, ManifestScene, PALETTE } from "../theme";

interface QuizRecapSceneProps {
  scene: ManifestScene;
  meta: LessonMeta;
  sceneNumber: number;
}

const LETTERS = ["A", "B", "C", "D", "E", "F"];

export const QuizRecapScene: React.FC<QuizRecapSceneProps> = ({
  scene,
  meta,
  sceneNumber,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const isVertical = height > width;
  const isPt = meta.language === "pt-BR";

  const revealStartFrame = Math.floor(scene.totalFrames * 0.6);
  const isRevealed = frame >= revealStartFrame;
  const revealSpring = spring({
    frame: Math.max(0, frame - revealStartFrame),
    fps,
    config: { damping: 18, stiffness: 120 },
  });

  const options = scene.options ?? [];
  const correctIndex = scene.correctIndex ?? 0;

  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        padding: isVertical ? "44px 48px" : "40px 92px",
        gap: 20,
      }}
    >
      <div>
        <div
          style={{
            fontFamily: FONTS.mono,
            fontSize: 18,
            fontWeight: 600,
            letterSpacing: "0.09em",
            textTransform: "uppercase",
            color: PALETTE.accent,
            marginBottom: 8,
          }}
        >
          {String(sceneNumber).padStart(2, "0")} / QUIZ RECAP
        </div>
        <h2
          style={{
            margin: 0,
            fontFamily: FONTS.serif,
            fontSize: isVertical ? 40 : 44,
            lineHeight: 1.2,
            color: PALETTE.ink,
          }}
        >
          {scene.question ?? scene.heading}
        </h2>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: isVertical ? "1fr" : "1fr 1fr",
          gap: 16,
        }}
      >
        {options.map((option, idx) => {
          const isCorrect = idx === correctIndex;
          const highlighted = isRevealed && isCorrect;
          const dimmed = isRevealed && !isCorrect;

          return (
            <div
              key={idx}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 16,
                backgroundColor: highlighted ? PALETTE.successSoft : PALETTE.panel,
                border: `2px solid ${highlighted ? PALETTE.success : PALETTE.border}`,
                borderRadius: 10,
                padding: isVertical ? "18px 20px" : "20px 24px",
                opacity: dimmed ? 0.55 : 1,
              }}
            >
              <div
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: 8,
                  flexShrink: 0,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontFamily: FONTS.mono,
                  fontWeight: 700,
                  fontSize: 20,
                  backgroundColor: highlighted ? PALETTE.success : PALETTE.ink,
                  color: PALETTE.bg,
                }}
              >
                {LETTERS[idx] ?? String(idx + 1)}
              </div>
              <div
                style={{
                  fontFamily: FONTS.sans,
                  fontSize: isVertical ? 24 : 24,
                  lineHeight: 1.35,
                  color: PALETTE.ink,
                  fontWeight: highlighted ? 600 : 400,
                }}
              >
                {option}
              </div>
            </div>
          );
        })}
      </div>

      {scene.explanation ? (
        <div
          style={{
            opacity: isRevealed ? revealSpring : 0,
            transform: `translateY(${isRevealed ? interpolate(revealSpring, [0, 1], [14, 0]) : 14}px)`,
            backgroundColor: PALETTE.successSoft,
            borderLeft: `6px solid ${PALETTE.success}`,
            borderRadius: 10,
            padding: "20px 26px",
            fontFamily: FONTS.sans,
            fontSize: isVertical ? 24 : 25,
            lineHeight: 1.45,
            color: PALETTE.ink,
          }}
        >
          <strong style={{ color: PALETTE.success }}>
            {isPt ? "Explicação: " : "Explanation: "}
          </strong>
          {scene.explanation}
        </div>
      ) : null}
    </div>
  );
};
