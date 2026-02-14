import { motion } from "framer-motion";

type Props = { value: number };

export function Countdown({ value }: Props) {
  return (
    <motion.section className="screen-card" key={value} initial={{ opacity: 0, scale: 0.85 }} animate={{ opacity: 1, scale: 1 }}>
      <h1 className="headline">GET READY!</h1>
      <motion.div className="count" initial={{ scaleX: 0.8, scaleY: 1.25 }} animate={{ scaleX: 1, scaleY: 1 }} transition={{ duration: 0.35 }}>
        {value}
      </motion.div>
      <h2 className="sub-headline">SMILE!</h2>
    </motion.section>
  );
}
