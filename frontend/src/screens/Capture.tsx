import { motion } from "framer-motion";

type Props = { flashing: boolean };

export function Capture({ flashing }: Props) {
  return (
    <motion.section className="screen-card" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <h1 className="headline">CAPTURING...</h1>
      <div className="camera-frame">
        <motion.div className="lens" animate={{ rotate: 360 }} transition={{ duration: 1.2, repeat: Infinity, ease: "linear" }} />
        <div className="photo-placeholder">SHUTTER MOMENT</div>
      </div>
      {flashing && <motion.div className="flash-overlay" initial={{ opacity: 0.95 }} animate={{ opacity: 0 }} transition={{ duration: 0.12 }} />}
    </motion.section>
  );
}
