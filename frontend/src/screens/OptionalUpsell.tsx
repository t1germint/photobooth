import { motion } from "framer-motion";

type Props = { open: boolean; onClose: () => void };

export function OptionalUpsell({ open, onClose }: Props) {
  if (!open) return null;

  return (
    <motion.div className="upsell-backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <motion.div className="upsell-card" initial={{ y: 80, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
        <h3>WANT MORE FUN?</h3>
        <div className="upsell-content">
          <div className="qr-box" />
          <div className="preview-mini" />
        </div>
        <motion.div className="arrow" animate={{ x: [0, 8, 0] }} transition={{ duration: 0.9, repeat: Infinity }}>➜</motion.div>
        <p className="cycle">SCAN FOR BONUS PHOTOS!</p>
        <button className="arcade-button alt" onClick={onClose}>CLOSE</button>
      </motion.div>
    </motion.div>
  );
}
