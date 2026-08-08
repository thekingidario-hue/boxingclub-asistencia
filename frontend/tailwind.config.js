/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'boxing-red': '#dc2626',
        'boxing-dark': '#0f0f0f',
        'boxing-gray': '#1a1a1a',
      },
    },
  },
  plugins: [],
}
