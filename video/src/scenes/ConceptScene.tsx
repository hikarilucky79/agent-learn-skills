import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { FONTS, ManifestScene, PALETTE } from "../theme";

interface ConceptSceneProps {
  scene: ManifestScene;
  sceneNumber: number;
}

export const ConceptScene: React.FC<ConceptSceneProps> = ({
  scene,
  sceneNumber,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const isVertical = height > width;

  const headerOpacity = interpolate(frame, [0, 12], [0, 1], {
    extrapolateRight: "clamp",
  });

  const bullets = scene.bullets ?? [];

  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        padding: isVertical ? "48px 52px" : "48px 96px",
        gap: 28,
      }}
    >
      <div style={{ opacity: headerOpacity }}>
        <div
          style={{
            fontFamily: FONTS.mono,
            fontSize: 18,
            fontWeight: 600,
            letterSpacing: "0.09em",
            textTransform: "uppercase",
            color: PALETTE.accent,
            marginBottom: 10,
          }}
        >
          {String(sceneNumber).padStart(2, "0")} / CONCEPT
        </div>
        <h2
          style={{
            margin: 0,
            fontFamily: FONTS.serif,
            fontSize: isVertical ? 48 : 54,
            lineHeight: 1.2,
            color: PALETTE.ink,
          }}
        >
          {scene.heading}
        </h2>
      </div>

      {scene.body ? (
        <p
          style={{
            margin: 0,
            fontFamily: FONTS.sans,
            fontSize: isVertical ? 30 : 31,
            lineHeight: 1.5,
            color: PALETTE.ink,
            maxWidth: isVertical ? "100%" : "90%",
          }}
        >
          {scene.body}
        </p>
      ) : null}

      {bullets.length > 0 ? (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 16,
            marginTop: 4,
          }}
        >
          {bullets.map((bullet, idx) => {
            const delay = 10 + idx * 14;
            const itemProgress = spring({
              frame: Math.max(0, frame - delay),
              fps,
              config: { damping: 20, stiffness: 120 },
            });
            const itemOpacity = interpolate(frame, [delay, delay + 10], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            const slideX = interpolate(itemProgress, [0, 1], [18, 0]);

            return (
              <div
                key={idx}
                style={{
                  backgroundColor: PALETTE.panel,
                  border: `1.5px solid ${PALETTE.border}`,
                  borderLeft: `6px solid ${PALETTE.accent}`,
                  borderRadius: 10,
                  padding: isVertical ? "20px 24px" : "20px 28px",
                  fontFamily: FONTS.sans,
                  fontSize: isVertical ? 26 : 27,
                  lineHeight: 1.45,
                  color: PALETTE.ink,
                  opacity: itemOpacity,
                  transform: `translateX(${slideX}px)`,
                }}
              >
                {bullet}
              </div>
            );
          })}
        </div>
      ) : null}

      {scene.formula ? (
        <div
          style={{
            marginTop: 8,
            backgroundColor: PALETTE.ink,
            color: PALETTE.codeText,
            borderRadius: 10,
            padding: "22px 28px",
            fontFamily: FONTS.mono,
            fontSize: isVertical ? 24 : 26,
            lineHeight: 1.45,
            border: `2px solid ${PALETTE.accent}`,
          }}
        >
          {scene.formula}
        </div>
      ) : null}
    </div>
  );
};
