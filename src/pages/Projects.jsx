import { motion } from 'framer-motion';
import { FaGithub, FaExternalLinkAlt } from 'react-icons/fa';

const projects = [
  {
    title: 'Project One',
    description:
      'A full-stack web application built with React and Node.js. Features include user authentication, real-time updates, and a responsive design.',
    technologies: ['React', 'Node.js', 'MongoDB', 'Socket.IO'],
    github: 'https://github.com/yourusername/project-one',
    live: 'https://project-one.com',
    image: '/project1.jpg',
  },
  {
    title: 'Project Two',
    description:
      'An e-commerce platform with a modern UI, shopping cart functionality, and secure payment processing.',
    technologies: ['Next.js', 'Stripe', 'Tailwind CSS', 'PostgreSQL'],
    github: 'https://github.com/yourusername/project-two',
    live: 'https://project-two.com',
    image: '/project2.jpg',
  },
  {
    title: 'Project Three',
    description:
      'A mobile-first web application for tracking personal finances and generating insights about spending habits.',
    technologies: ['React Native', 'Firebase', 'Chart.js', 'Express'],
    github: 'https://github.com/yourusername/project-three',
    live: 'https://project-three.com',
    image: '/project3.jpg',
  },
];

function Projects() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="section-container"
    >
      <h1 className="heading-primary">My Projects</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {projects.map((project, index) => (
          <motion.div
            key={project.title}
            initial={{ opacity: 0, rotateY: 90, z: -200 }}
            animate={{ opacity: 1, rotateY: 0, z: 0 }}
            transition={{ 
              delay: index * 0.3,
              duration: 1,
              type: "spring",
              stiffness: 40,
              damping: 8
            }}
            whileHover={{ 
              scale: 1.1,
              rotateY: 15,
              z: 100,
              boxShadow: "0 20px 30px rgba(0,0,0,0.2)",
              transition: { 
                duration: 0.4,
                type: "spring",
                stiffness: 300
              }
            }}
            style={{ perspective: 1000 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden transform-gpu"
          >
            <motion.div
              whileHover={{
                scale: 1.1,
                transition: { duration: 0.2 }
              }}
              className="aspect-w-16 aspect-h-9 bg-gray-200 dark:bg-gray-700"
            >
              <img
                src={project.image}
                alt={project.title}
                className="object-cover w-full h-48 transform-gpu"
              />
            </motion.div>
            <div className="p-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {project.title}
              </h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">{project.description}</p>
              <div className="flex flex-wrap gap-2 mb-4">
                {project.technologies.map((tech) => (
                  <span
                    key={tech}
                    className="px-2 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
                  >
                    {tech}
                  </span>
                ))}
              </div>
              <div className="flex space-x-4">
                <a
                  href={project.github}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-gray-600 dark:text-gray-300 hover:text-primary-500 dark:hover:text-primary-400"
                >
                  <FaGithub className="h-5 w-5 mr-2" />
                  Code
                </a>
                <a
                  href={project.live}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-gray-600 dark:text-gray-300 hover:text-primary-500 dark:hover:text-primary-400"
                >
                  <FaExternalLinkAlt className="h-4 w-4 mr-2" />
                  Live Demo
                </a>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

export default Projects;
