import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { FONTS, LessonMeta, ManifestScene, PALETTE } from "../theme";

interface IntroSceneProps {
  scene: ManifestScene;
  meta: LessonMeta;
}

export const IntroScene: React.FC<IntroSceneProps> = ({ scene, meta }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const isVertical = height > width;

  const entrance = spring({
    frame,
    fps,
    config: { damping: 18, stiffness: 110 },
  });

  const translateY = interpolate(entrance, [0, 1], [28, 0]);
  const opacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        padding: isVertical ? "64px 56px" : "72px 110px",
        opacity,
        transform: `translateY(${translateY}px)`,
      }}
    >
      <div
        style={{
          alignSelf: "flex-start",
          backgroundColor: PALETTE.accentSoft,
          color: PALETTE.accent,
          border: `1.5px solid ${PALETTE.accent}`,
          borderRadius: 6,
          padding: "8px 18px",
          fontFamily: FONTS.mono,
          fontSize: isVertical ? 22 : 20,
          fontWeight: 600,
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          marginBottom: 28,
        }}
      >
        {meta.discipline}
      </div>

      <h1
        style={{
          margin: 0,
          fontFamily: FONTS.serif,
          fontSize: isVertical ? 64 : 74,
          lineHeight: 1.15,
          fontWeight: 700,
          color: PALETTE.ink,
          maxWidth: isVertical ? "100%" : "88%",
        }}
      >
        {scene.heading}
      </h1>

      <div
        style={{
          width: 112,
          height: 5,
          backgroundColor: PALETTE.accent,
          marginTop: 32,
          marginBottom: 32,
          borderRadius: 3,
        }}
      />

      {scene.subtitle ? (
        <p
          style={{
            margin: 0,
            fontFamily: FONTS.sans,
            fontSize: isVertical ? 34 : 36,
            lineHeight: 1.4,
            fontWeight: 500,
            color: PALETTE.ink,
            maxWidth: isVertical ? "100%" : "82%",
          }}
        >
          {scene.subtitle}
        </p>
      ) : null}

      {scene.body ? (
        <div
          style={{
            marginTop: 28,
            padding: "22px 28px",
            backgroundColor: PALETTE.panel,
            borderLeft: `5px solid ${PALETTE.accent}`,
            borderRadius: 8,
            fontFamily: FONTS.sans,
            fontSize: isVertical ? 26 : 26,
            lineHeight: 1.5,
            color: PALETTE.muted,
            maxWidth: isVertical ? "100%" : "78%",
          }}
        >
          {scene.body}
        </div>
      ) : null}
    </div>
  );
};
