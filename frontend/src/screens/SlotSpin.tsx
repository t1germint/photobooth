import { motion } from "framer-motion";

type Props = { reels: string[][]; spinning: boolean };

export function SlotSpin({ reels, spinning }: Props) {
  return (
    <motion.section className="screen-card" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}>
      <h1 className="headline wiggle">SPINNING MODES...</h1>
      <div className={`slot-machine ${spinning ? "spinning" : ""}`}>
        {reels.map((reel, i) => (
          <div className="reel" key={i}>
            {reel.map((label, idx) => (
              <div className="reel-item" key={`${label}-${idx}`}>{label}</div>
            ))}
          </div>
        ))}
      </div>
    </motion.section>
  );
}
