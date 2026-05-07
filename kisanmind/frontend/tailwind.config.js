// tailwind.config.js
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "hsl(150, 85%, 30%)",
        secondary: "hsl(45, 70%, 50%)",
        accent: "hsl(210, 80%, 55%)",
        background: "hsl(210, 15%, 98%)",
        glass: "rgba(255,255,255,0.15)"
      },
      backdropBlur: { xs: "2px", sm: "4px", md: "8px" },
      borderRadius: { xs: "0.25rem", sm: "0.5rem", lg: "1rem" }
    }
  },
  plugins: []
};
