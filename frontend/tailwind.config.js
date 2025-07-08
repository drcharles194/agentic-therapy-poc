/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary brand colors based on #8a2be2 (blueviolet)
        brand: {
          primary: '#8a2be2',    // Original blueviolet
          dark: '#6a1ba2',       // Darker purple
          light: '#a855f7',      // Lighter purple
        },
        
        // Pastel palette inspired by the brand colors
        pastel: {
          // Purple family - main brand colors in pastel
          'purple-50': '#faf7ff',   // Almost white with purple hint
          'purple-100': '#f3e8ff',  // Very light purple
          'purple-200': '#e9d5ff',  // Light purple
          'purple-300': '#d8b4fe',  // Soft purple
          'purple-400': '#c084fc',  // Medium pastel purple
          'purple-500': '#a855f7',  // Brand purple
          'purple-600': '#8a2be2',  // Primary brand
          'purple-700': '#7c3aed',  // Darker purple
          'purple-800': '#6b21a8',  // Deep purple
          'purple-900': '#4c1d95',  // Very dark purple
          
          // Complementary pastels
          'peach-50': '#fff9f5',    // Very light peach
          'peach-100': '#fef2e6',   // Light peach
          'peach-200': '#fde5cc',   // Soft peach
          'peach-300': '#fbd199',   // Medium peach
          'peach-400': '#f9b366',   // Warm peach
          
          'mint-50': '#f0fdf9',     // Very light mint
          'mint-100': '#e6fffa',    // Light mint
          'mint-200': '#c6f7e9',    // Soft mint
          'mint-300': '#9ae6d8',    // Medium mint
          'mint-400': '#6dd4c7',    // Fresh mint
          
          'lavender-50': '#f8f7ff', // Very light lavender
          'lavender-100': '#f1edff', // Light lavender
          'lavender-200': '#e4d9ff', // Soft lavender
          'lavender-300': '#d0bfff', // Medium lavender
          'lavender-400': '#b8a3ff', // Warm lavender
          
          'cream-50': '#fffef7',    // Almost white cream
          'cream-100': '#fffbeb',   // Very light cream
          'cream-200': '#fef3c7',   // Light cream
          'cream-300': '#fde68a',   // Soft cream
          'cream-400': '#fcd34d',   // Medium cream
        },
        
        // Refined grays that work with pastels and black
        neutral: {
          '50': '#fafafa',    // Almost white
          '100': '#f5f5f5',   // Very light gray
          '200': '#e5e5e5',   // Light gray
          '300': '#d4d4d4',   // Soft gray
          '400': '#a3a3a3',   // Medium gray
          '500': '#737373',   // Standard gray
          '600': '#525252',   // Dark gray
          '700': '#404040',   // Darker gray
          '800': '#262626',   // Very dark gray
          '900': '#171717',   // Almost black
          '950': '#0a0a0a',   // Near black
        },
        
        // Updated collaborative theme colors
        collaborative: {
          primary: '#8a2be2',     // Main brand color
          secondary: '#a855f7',   // Lighter purple
          accent: '#fcd34d',      // Soft cream accent
          success: '#6dd4c7',     // Mint green
          warning: '#f9b366',     // Soft peach
          error: '#f87171',       // Soft red
          neutral: '#737373',     // Medium gray
          background: '#faf7ff',  // Very light purple background
          surface: '#ffffff',     // Pure white
          text: '#171717',        // Near black for text
          'text-light': '#525252', // Dark gray for secondary text
        }
      },
      fontFamily: {
        'heading': ['Lora', 'serif'],
        'sans': ['Poppins', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '0.7' },
          '50%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
} 