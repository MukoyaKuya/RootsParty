/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './**/forms.py',
    './**/views.py',
  ],
  theme: {
    extend: {
      colors: {
        roots: {
          black: '#1a1a1a',
          red: '#E60000',
          white: '#FFFFFF',
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
    },
  },
  plugins: [],
}
