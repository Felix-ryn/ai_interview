// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  // Path ini memberitahu Tailwind di mana harus mencari kelas yang digunakan
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}