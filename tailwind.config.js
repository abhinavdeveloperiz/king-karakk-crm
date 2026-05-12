/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./app/templates/**/*.html",
  ],

  theme: {
    extend: {
      backgroundImage: {
        'gradient-primary':
          "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      },
    },
  },

  plugins: [],
}