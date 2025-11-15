import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#137fec',
        'background-light': '#f6f7f8',
        'background-dark': '#101922',
        'component-dark': '#1a2633',
        'card-dark': '#16222e',
        'border-dark': '#233648',
        'text-primary-dark': '#EAEAEA',
        'text-secondary-dark': '#92adc9',
        success: '#38A169',
        'success-alt': '#2ECC71',
        error: '#E74C3C',
        danger: '#E53E3E',
        warning: '#DD6B20',
      },
      fontFamily: {
        display: ['Space Grotesk', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '0.25rem',
        lg: '0.5rem',
        xl: '0.75rem',
        full: '9999px',
      },
    },
  },
  plugins: [],
}
export default config

