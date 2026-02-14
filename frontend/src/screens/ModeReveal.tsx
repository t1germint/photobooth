import { motion } from "framer-motion";

type Props = { mode: string };

export function ModeReveal({ mode }: Props) {
  return (
    <motion.section className="screen-card" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}>
      <motion.h1 className="headline" initial={{ scale: 0.6 }} animate={{ scale: 1.05 }} transition={{ type: "spring", stiffness: 250, damping: 11 }}>
        YOU'RE A
      </motion.h1>
      <h2 className="mode-title">{mode}!</h2>
      <p className="pose">POSE WITH POWER!</p>
    </motion.section>
  );
}
