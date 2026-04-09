import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#00d4aa",
          purple: "#7c3aed",
          bg: "#0a0a0f",
          surface: "#12121a",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        "grad-hero":
          "radial-gradient(circle at 20% 20%, rgba(124,58,237,0.25), transparent 50%), radial-gradient(circle at 80% 80%, rgba(0,212,170,0.18), transparent 50%)",
      },
      animation: {
        "fade-up": "fadeUp .6s ease-out both",
        "float": "float 6s ease-in-out infinite",
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        float: {
          "0%,100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-14px)" },
        },
      },
    },
  },
  plugins: [],
};
export default config;
