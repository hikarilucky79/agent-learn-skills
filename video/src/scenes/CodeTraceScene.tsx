import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { FONTS, ManifestScene, PALETTE } from "../theme";

interface CodeTraceSceneProps {
  scene: ManifestScene;
  sceneNumber: number;
}

export const CodeTraceScene: React.FC<CodeTraceSceneProps> = ({
  scene,
  sceneNumber,
}) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const isVertical = height > width;

  const lines = (scene.code ?? "").split("\n");
  const traceOrder =
    scene.highlightLines && scene.highlightLines.length > 0
      ? scene.highlightLines
      : lines.map((_, idx) => idx + 1);

  const stepIndex = Math.min(
    traceOrder.length - 1,
    Math.floor(
      interpolate(frame, [0, Math.max(1, scene.durationFrames - 12)], [0, traceOrder.length], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    )
  );
  const activeLine = traceOrder[stepIndex] ?? 1;

  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        padding: isVertical ? "48px 48px" : "44px 92px",
        gap: 24,
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
          {String(sceneNumber).padStart(2, "0")} / CODE TRACE
        </div>
        <h2
          style={{
            margin: 0,
            fontFamily: FONTS.serif,
            fontSize: isVertical ? 44 : 50,
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
            fontSize: isVertical ? 26 : 26,
            color: PALETTE.muted,
            lineHeight: 1.45,
          }}
        >
          {scene.body}
        </p>
      ) : null}

      <div
        style={{
          backgroundColor: PALETTE.codeBg,
          color: PALETTE.codeText,
          borderRadius: 12,
          border: `2px solid ${PALETTE.ink}`,
          overflow: "hidden",
          boxShadow: "0 14px 36px rgba(38, 40, 33, 0.12)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "14px 24px",
            borderBottom: "1px solid #3a3b33",
            backgroundColor: "#1d1e18",
            fontFamily: FONTS.mono,
            fontSize: 18,
            color: "#c9c7bc",
          }}
        >
          <span>{(scene.codeLanguage ?? "code").toUpperCase()}</span>
          <span>
            Line {activeLine} / {lines.length}
          </span>
        </div>

        <div style={{ padding: "22px 0" }}>
          {lines.map((lineText, idx) => {
            const lineNum = idx + 1;
            const isHighlighted = lineNum === activeLine;
            return (
              <div
                key={lineNum}
                style={{
                  display: "flex",
                  alignItems: "baseline",
                  padding: isVertical ? "10px 22px" : "10px 28px",
                  backgroundColor: isHighlighted
                    ? "rgba(145, 65, 44, 0.34)"
                    : "transparent",
                  borderLeft: isHighlighted
                    ? `6px solid ${PALETTE.accent}`
                    : "6px solid transparent",
                  fontFamily: FONTS.mono,
                  fontSize: isVertical ? 24 : 28,
                  lineHeight: 1.5,
                }}
              >
                <span
                  style={{
                    width: 52,
                    flexShrink: 0,
                    color: isHighlighted ? "#f5f3ed" : "#7c7d73",
                    fontWeight: isHighlighted ? 700 : 400,
                    userSelect: "none",
                  }}
                >
                  {String(lineNum).padStart(2, "0")}
                </span>
                <span
                  style={{
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                    color: isHighlighted ? "#ffffff" : "#dcdad0",
                    fontWeight: isHighlighted ? 600 : 400,
                  }}
                >
                  {lineText || " "}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
