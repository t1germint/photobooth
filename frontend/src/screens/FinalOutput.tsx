import { motion } from "framer-motion";

type Props = {
  onTryAnother: () => void;
};

export function FinalOutput({ onTryAnother }: Props) {
  return (
    <motion.section className="screen-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <motion.div className="final-frame" initial={{ x: -80, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ duration: 0.45 }}>
        <div className="shine" />
        <div className="kid-photo" />
      </motion.div>
      <motion.div className="sticker-caption" initial={{ scale: 0.8, rotate: -3 }} animate={{ scale: 1, rotate: -1 }} transition={{ type: "spring", stiffness: 220 }}>
        SUPERHEROES! POWER POSE!
      </motion.div>
      <div className="actions">
        <button className="arcade-button">PRINT</button>
        <button className="arcade-button">DOWNLOAD</button>
        <button className="arcade-button alt" onClick={onTryAnother}>TRY ANOTHER MODE</button>
      </div>
    </motion.section>
  );
}
