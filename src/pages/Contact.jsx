import { motion } from 'framer-motion';
import { useState } from 'react';
import { FaEnvelope, FaGithub, FaLinkedin, FaTwitter } from 'react-icons/fa';

function Contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: '',
  });

  const formFields = [
    { name: 'name', label: 'Name', type: 'text' },
    { name: 'email', label: 'Email', type: 'email' },
    { name: 'message', label: 'Message', type: 'textarea' },
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    // Here you would typically handle the form submission
    console.log('Form submitted:', formData);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="section-container"
    >
      <div className="max-w-3xl mx-auto">
        <h1 className="heading-primary">Get in Touch</h1>
        <p className="paragraph mb-8">
          I'm always open to new opportunities and collaborations. Feel free to reach out!
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h2 className="heading-secondary">Contact Information</h2>
            <div className="space-y-4">
              <a
                href="mailto:your.email@example.com"
                className="flex items-center space-x-3 text-gray-600 dark:text-gray-300 hover:text-primary-500 dark:hover:text-primary-400"
              >
                <FaEnvelope className="h-5 w-5" />
                <span>your.email@example.com</span>
              </a>
              <a
                href="https://github.com/yourusername"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-3 text-gray-600 dark:text-gray-300 hover:text-primary-500 dark:hover:text-primary-400"
              >
                <FaGithub className="h-5 w-5" />
                <span>GitHub</span>
              </a>
              <a
                href="https://linkedin.com/in/yourusername"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-3 text-gray-600 dark:text-gray-300 hover:text-primary-500 dark:hover:text-primary-400"
              >
                <FaLinkedin className="h-5 w-5" />
                <span>LinkedIn</span>
              </a>
              <a
                href="https://twitter.com/yourusername"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-3 text-gray-600 dark:text-gray-300 hover:text-primary-500 dark:hover:text-primary-400"
              >
                <FaTwitter className="h-5 w-5" />
                <span>Twitter</span>
              </a>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="grid md:grid-cols-1 gap-12">
              <motion.div
                initial={{ opacity: 0, x: -100, rotateY: -45, z: -200 }}
                animate={{ opacity: 1, x: 0, rotateY: 0, z: 0 }}
                transition={{ 
                  duration: 1,
                  type: "spring",
                  stiffness: 50,
                  damping: 10
                }}
                className="transform-gpu"
              >
                <h2 className="heading-secondary mb-6">Get in Touch</h2>
                <motion.form 
                  onSubmit={handleSubmit}
                  className="space-y-6"
                >
                  {formFields.map((field, index) => (
                    <motion.div
                      key={field.name}
                      initial={{ opacity: 0, y: 50, z: -50 }}
                      animate={{ opacity: 1, y: 0, z: 0 }}
                      transition={{ 
                        delay: index * 0.2,
                        duration: 0.8,
                        type: "spring",
                        stiffness: 70
                      }}
                      whileHover={{ 
                        scale: 1.02,
                        z: 20,
                        transition: { duration: 0.2 }
                      }}
                      className="transform-gpu"
                    >
                      <label 
                        htmlFor={field.name}
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                      >
                        {field.label}
                      </label>
                      {field.type === 'textarea' ? (
                        <motion.textarea
                          whileFocus={{ 
                            scale: 1.02,
                            z: 30,
                            boxShadow: "0 10px 20px rgba(0,0,0,0.1)",
                            transition: { duration: 0.2 }
                          }}
                          id={field.name}
                          name={field.name}
                          rows={4}
                          className="form-input"
                          value={formData[field.name]}
                          onChange={handleChange}
                          required
                        />
                      ) : (
                        <motion.input
                          whileFocus={{ 
                            scale: 1.02,
                            z: 30,
                            boxShadow: "0 10px 20px rgba(0,0,0,0.1)",
                            transition: { duration: 0.2 }
                          }}
                          type={field.type}
                          id={field.name}
                          name={field.name}
                          className="form-input"
                          value={formData[field.name]}
                          onChange={handleChange}
                          required
                        />
                      )}
                    </motion.div>
                  ))}
                  <motion.button
                    type="submit"
                    whileHover={{ 
                      scale: 1.05,
                      rotateY: 5,
                      z: 50,
                      boxShadow: "0 15px 25px rgba(0,0,0,0.2)",
                      transition: { duration: 0.3 }
                    }}
                    whileTap={{ scale: 0.95 }}
                    className="button-primary w-full transform-gpu"
                  >
                    Send Message
                  </motion.button>
                </motion.form>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}

export default Contact;
