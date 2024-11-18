import { motion } from 'framer-motion';
import { FaCode, FaLaptopCode, FaServer } from 'react-icons/fa';

const skills = [
  {
    category: 'Frontend Development',
    icon: FaCode,
    items: ['React', 'JavaScript', 'HTML/CSS', 'Tailwind CSS', 'TypeScript'],
  },
  {
    category: 'Backend Development',
    icon: FaServer,
    items: ['Node.js', 'Python', 'SQL', 'RESTful APIs', 'GraphQL'],
  },
  {
    category: 'Tools & Technologies',
    icon: FaLaptopCode,
    items: ['Git', 'Docker', 'AWS', 'VS Code', 'Agile/Scrum'],
  },
];

function About() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="section-container"
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h1 className="heading-primary">About Me</h1>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <p className="paragraph mb-4">
              I'm a passionate software developer with a strong foundation in both frontend
              and backend development. I love creating elegant solutions to complex problems
              and am constantly learning new technologies.
            </p>
            <p className="paragraph mb-4">
              With experience in building modern web applications, I focus on writing clean,
              maintainable code that delivers great user experiences.
            </p>
            <p className="paragraph">
              When I'm not coding, you can find me exploring new technologies, contributing
              to open-source projects, or sharing my knowledge with the developer community.
            </p>
          </div>
          <div>
            <h2 className="heading-secondary mb-6">Skills & Expertise</h2>
            <div className="space-y-8">
              {skills.map((skillSet) => (
                <motion.div
                  key={skillSet.category}
                  initial={{ opacity: 0, rotateX: 45, y: 50, z: -50 }}
                  animate={{ opacity: 1, rotateX: 0, y: 0, z: 0 }}
                  transition={{ 
                    duration: 0.8,
                    type: "spring",
                    stiffness: 100
                  }}
                  whileHover={{ 
                    scale: 1.02,
                    rotateX: 5,
                    z: 20,
                    transition: { duration: 0.2 }
                  }}
                  style={{ perspective: 1000 }}
                  className="space-y-2 transform-gpu"
                >
                  <div className="flex items-center space-x-2">
                    <skillSet.icon className="h-5 w-5 text-primary-500" />
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {skillSet.category}
                    </h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {skillSet.items.map((item, index) => (
                      <motion.span
                        key={item}
                        initial={{ opacity: 0, y: 20, z: -20 }}
                        animate={{ opacity: 1, y: 0, z: 0 }}
                        transition={{ delay: index * 0.1, duration: 0.5 }}
                        whileHover={{ 
                          scale: 1.1,
                          z: 10,
                          transition: { duration: 0.2 }
                        }}
                        className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full transform-gpu"
                      >
                        {item}
                      </motion.span>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

export default About;
