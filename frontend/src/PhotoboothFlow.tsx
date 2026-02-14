import { AnimatePresence, motion } from "framer-motion";
import confetti from "canvas-confetti";
import { useEffect, useMemo, useRef, useState } from "react";
import { Countdown } from "./screens/Countdown";
import { Capture } from "./screens/Capture";
import { FinalOutput } from "./screens/FinalOutput";
import { IdleDisplay } from "./screens/IdleDisplay";
import { ModeReveal } from "./screens/ModeReveal";
import { OptionalUpsell } from "./screens/OptionalUpsell";
import { SlotSpin } from "./screens/SlotSpin";
import { BoothScreen, MODES } from "./types";

const transition = { duration: 0.42, ease: [0.22, 1, 0.36, 1] };

function randomReels(): string[][] {
  return new Array(3).fill(null).map(() =>
    new Array(3).fill(null).map(() => MODES[Math.floor(Math.random() * MODES.length)]),
  );
}

export function PhotoboothFlow() {
  const [screen, setScreen] = useState<BoothScreen>(BoothScreen.IdleDisplay);
  const [mode, setMode] = useState("SUPERHERO");
  const [reels, setReels] = useState<string[][]>(() => randomReels());
  const [countdown, setCountdown] = useState(3);
  const [flash, setFlash] = useState(false);
  const [showUpsell, setShowUpsell] = useState(false);
  const spinIntervalRef = useRef<number | null>(null);

  useEffect(() => {
    const subtle = window.setInterval(() => {
      confetti({
        particleCount: 2,
        spread: 55,
        startVelocity: 10,
        gravity: 0.65,
        origin: { x: Math.random(), y: Math.random() * 0.35 },
        colors: ["#ff4fcf", "#4fd8ff", "#ffd84d", "#ffffff"],
        scalar: 0.55,
      });
    }, 900);

    return () => window.clearInterval(subtle);
  }, []);

  useEffect(() => {
    if (screen === BoothScreen.SlotSpin) {
      spinIntervalRef.current = window.setInterval(() => setReels(randomReels()), 120);
      const stopTimer = window.setTimeout(() => {
        if (spinIntervalRef.current) window.clearInterval(spinIntervalRef.current);
        const picked = MODES[Math.floor(Math.random() * MODES.length)];
        setMode(picked);
        confetti({ particleCount: 80, spread: 80, origin: { y: 0.2 }, colors: ["#ff4fcf", "#4fd8ff", "#ffd84d"] });
        setScreen(BoothScreen.ModeReveal);
      }, 2500);
      return () => {
        if (spinIntervalRef.current) window.clearInterval(spinIntervalRef.current);
        window.clearTimeout(stopTimer);
      };
    }

    if (screen === BoothScreen.ModeReveal) {
      const t = window.setTimeout(() => setScreen(BoothScreen.Countdown), 1200);
      return () => window.clearTimeout(t);
    }

    if (screen === BoothScreen.Countdown) {
      setCountdown(3);
      const ticks = [
        window.setTimeout(() => setCountdown(2), 1000),
        window.setTimeout(() => setCountdown(1), 2000),
        window.setTimeout(() => setScreen(BoothScreen.Capture), 3000),
      ];
      return () => ticks.forEach(window.clearTimeout);
    }

    if (screen === BoothScreen.Capture) {
      const flashIn = window.setTimeout(() => setFlash(true), 500);
      const flashOut = window.setTimeout(() => setFlash(false), 650);
      const done = window.setTimeout(() => setScreen(BoothScreen.FinalOutput), 1500);
      return () => {
        window.clearTimeout(flashIn);
        window.clearTimeout(flashOut);
        window.clearTimeout(done);
      };
    }

    if (screen === BoothScreen.FinalOutput) {
      const upsellTimer = window.setTimeout(() => setShowUpsell(true), 2000);
      return () => window.clearTimeout(upsellTimer);
    }

    return undefined;
  }, [screen]);

  const view = useMemo(() => {
    switch (screen) {
      case BoothScreen.IdleDisplay:
        return <IdleDisplay onStart={() => setScreen(BoothScreen.SlotSpin)} />;
      case BoothScreen.SlotSpin:
        return <SlotSpin reels={reels} spinning />;
      case BoothScreen.ModeReveal:
        return <ModeReveal mode={mode} />;
      case BoothScreen.Countdown:
        return <Countdown value={countdown} />;
      case BoothScreen.Capture:
        return <Capture flashing={flash} />;
      case BoothScreen.FinalOutput:
        return (
          <FinalOutput
            onTryAnother={() => {
              setShowUpsell(false);
              setScreen(BoothScreen.SlotSpin);
            }}
          />
        );
      default:
        return null;
    }
  }, [screen, reels, mode, countdown, flash]);

  return (
    <div className="booth-root">
      <AnimatePresence mode="wait">
        <motion.div key={screen} initial={{ opacity: 0, scale: 0.98, y: 16 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.98, y: -16 }} transition={transition}>
          {view}
        </motion.div>
      </AnimatePresence>
      <OptionalUpsell open={showUpsell && screen === BoothScreen.FinalOutput} onClose={() => setShowUpsell(false)} />
    </div>
  );
}
