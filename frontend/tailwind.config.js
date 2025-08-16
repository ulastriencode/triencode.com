export default {
  content: ["./index.html","./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "rgb(var(--color-primary-rgb, 30 58 138) / <alpha-value>)",
        },
        accent: "rgb(var(--color-accent-rgb, 34 211 238) / <alpha-value>)",
      },
    },
  },
  plugins: [],
};
