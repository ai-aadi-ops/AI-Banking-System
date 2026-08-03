import { motion } from "framer-motion";
import BalanceCard from "./BalanceCard";
import RecommendationCard from "./RecommendationCard";

export default function HeroDashboard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      className="grid md:grid-cols-2 gap-6 mt-16"
    >

     <BalanceCard />

     <RecommendationCard />

    </motion.div>
  );
}
