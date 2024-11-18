import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { FaArrowRight } from 'react-icons/fa';

function Home() {
  return (
    <motion.div
      initial={{ opacity: 0, rotateX: 80, perspective: 1000, y: 100, scale: 0.8 }}
      animate={{ opacity: 1, rotateX: 0, y: 0, scale: 1 }}
      exit={{ opacity: 0, rotateX: -80, y: -100, scale: 0.8 }}
      transition={{ 
        duration: 1,
        type: "spring",
        stiffness: 50,
        damping: 10
      }}
      style={{ perspective: 1000 }}
      className="transform-gpu"
    >
      <div className="section-container">
        <div className="max-w-4xl">
          <motion.h1
            className="heading-primary"
            initial={{ opacity: 0, z: -200, rotateY: 90 }}
            animate={{ opacity: 1, z: 0, rotateY: 0 }}
            transition={{ 
              delay: 0.3,
              duration: 1.2,
              type: "spring",
              stiffness: 60
            }}
            style={{ perspective: 1000 }}
          >
            Hi, I'm Jay Ravichandran
          </motion.h1>
          <motion.p
            className="paragraph mb-8"
            initial={{ opacity: 0, rotateY: -90, x: -100 }}
            animate={{ opacity: 1, rotateY: 0, x: 0 }}
            transition={{ 
              delay: 0.6,
              duration: 1,
              type: "spring",
              stiffness: 50
            }}
            style={{ perspective: 1000 }}
          >
            Welcome to my personal website! I'm passionate about technology and innovation.
            I love building things that make a difference.
          </motion.p>
          <motion.div
            className="flex space-x-4"
            initial={{ opacity: 0, scale: 0.5, z: -200 }}
            animate={{ opacity: 1, scale: 1, z: 0 }}
            transition={{ 
              delay: 0.9,
              duration: 0.8,
              type: "spring",
              stiffness: 80
            }}
          >
            <motion.div
              whileHover={{ 
                scale: 1.1,
                rotateY: 15,
                z: 100,
                transition: { duration: 0.3 }
              }}
              className="transform-gpu"
            >
              <Link to="/projects" className="button-primary">
                View My Work
                <FaArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </motion.div>
            <motion.div
              whileHover={{ 
                scale: 1.1,
                rotateY: -15,
                z: 100,
                transition: { duration: 0.3 }
              }}
              className="transform-gpu"
            >
              <Link to="/contact" className="button-secondary">
                Get in Touch
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}

export default Home;
