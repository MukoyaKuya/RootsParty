/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './core/templates/**/*.html',
    './users/templates/**/*.html',
    './finance/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        roots: {
          black: '#000000',
          red: '#E60000',
          white: '#FFFFFF',
          green: '#22c55e',
        }
      },
      fontFamily: {
        sans: ['Oswald', 'system-ui', 'sans-serif'],
        display: ['Oswald', 'system-ui', 'sans-serif'],
      },
      borderWidth: {
        '3': '3px',
        '4': '4px',
      }
    }
  },
  plugins: [],
}
