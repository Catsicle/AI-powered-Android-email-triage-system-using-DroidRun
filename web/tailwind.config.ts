import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Obsidian Professional Theme
        bg: {
          primary: "#121212",    // Matte Black
          secondary: "#1E1E1E",  // Dark Charcoal
          card: "#1E1E1E",
        },
        text: {
          primary: "#FFFFFF",    // Primary White
          secondary: "#A0A0A0",  // Cool Grey
          muted: "#6B6B6B",
        },
        accent: {
          decisions: "#2979FF",  // Electric Blue
          urgent: "#FFAB00",     // Amber
          spam: "#EF5350",       // Desaturated Red
          safe: "#00E676",       // Emerald Green
          calendar: "#00E676",
          info: "#64B5F6",       // Light Blue
        },
      },
      fontFamily: {
        sans: ["Inter", "Roboto", "sans-serif"],
        mono: ["Roboto Mono", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
