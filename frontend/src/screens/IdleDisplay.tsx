import { motion } from "framer-motion";

type Props = { onStart: () => void };

export function IdleDisplay({ onStart }: Props) {
  return (
    <motion.section className="screen-card idle" initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }}>
      <div className="spark-layer" />
      <h1 className="headline">STEP IN.</h1>
      <h2 className="sub-headline pulse-shimmer">PRESS START!</h2>
      <button className="arcade-button" onClick={onStart}>START</button>
    </motion.section>
  );
}
