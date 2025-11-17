#!/usr/bin/env node
/**
 * Alpine Analytics Brand Asset Generator
 * Generates branded assets from templates using brand config
 */

const fs = require('fs');
const path = require('path');

// Brand configuration (matching brand.ts)
// NOTE: Keep this in sync with alpine-frontend/lib/brand.ts
const AlpineBrand = {
  colors: {
    black: {
      pure: '#000000',
      primary: '#0a0a0f',
      secondary: '#0f0f1a',
      tertiary: '#15151a',
      border: '#1a1a2e',
    },
    neon: {
      cyan: '#18e0ff',
      cyanDark: '#00b8d4',
      pink: '#fe1c80',
      pinkDark: '#cc0066',
      purple: '#9600ff',
      purpleDark: '#5320f9',
      orange: '#ff5f01',
      orangeDark: '#cc4d00',
    },
    gradients: {
      primary: 'linear-gradient(90deg, #18e0ff 0%, #fe1c80 50%, #9600ff 100%)',
      cyanPink: 'linear-gradient(90deg, #18e0ff 0%, #fe1c80 100%)',
      pinkPurple: 'linear-gradient(90deg, #fe1c80 0%, #9600ff 100%)',
      pulse: 'linear-gradient(135deg, #18e0ff 0%, #fe1c80 50%, #9600ff 100%)',
    },
    semantic: {
      success: '#00ff88',
      error: '#ff2d55',
      warning: '#ff5f01',
      info: '#18e0ff',
    },
    text: {
      primary: '#ffffff',
      secondary: '#a1a1aa',
      tertiary: '#71717a',
      inverse: '#000000',
    },
  },
  metadata: {
    name: 'Alpine Analytics LLC',
    tagline: 'Adaptive AI Trading Signals',
    taglineShort: 'Provably.',
    website: 'https://alpineanalytics.com',
    email: 'info@alpineanalytics.com',
    trademark: 'Alpine Analytics®',
  },
};

// Generate CSS variables file
function generateCSSVariables() {
  const css = `
/* Alpine Analytics Brand CSS Variables */
:root {
  /* Black Scale */
  --alpine-black-pure: ${AlpineBrand.colors.black.pure};
  --alpine-black-primary: ${AlpineBrand.colors.black.primary};
  --alpine-black-secondary: ${AlpineBrand.colors.black.secondary};
  --alpine-black-tertiary: ${AlpineBrand.colors.black.tertiary};
  --alpine-black-border: ${AlpineBrand.colors.black.border};
  
  /* Neon Colors */
  --alpine-neon-cyan: ${AlpineBrand.colors.neon.cyan};
  --alpine-neon-cyan-dark: ${AlpineBrand.colors.neon.cyanDark};
  --alpine-neon-pink: ${AlpineBrand.colors.neon.pink};
  --alpine-neon-pink-dark: ${AlpineBrand.colors.neon.pinkDark};
  --alpine-neon-purple: ${AlpineBrand.colors.neon.purple};
  --alpine-neon-purple-dark: ${AlpineBrand.colors.neon.purpleDark};
  --alpine-neon-orange: ${AlpineBrand.colors.neon.orange};
  --alpine-neon-orange-dark: ${AlpineBrand.colors.neon.orangeDark};
  
  /* Semantic Colors */
  --alpine-semantic-success: ${AlpineBrand.colors.semantic.success};
  --alpine-semantic-error: ${AlpineBrand.colors.semantic.error};
  --alpine-semantic-warning: ${AlpineBrand.colors.semantic.warning};
  --alpine-semantic-info: ${AlpineBrand.colors.semantic.info};
  
  /* Text Colors */
  --alpine-text-primary: ${AlpineBrand.colors.text.primary};
  --alpine-text-secondary: ${AlpineBrand.colors.text.secondary};
  --alpine-text-tertiary: ${AlpineBrand.colors.text.tertiary};
  --alpine-text-inverse: ${AlpineBrand.colors.text.inverse};
}
`;
  
  const outputPath = path.join(__dirname, '..', 'alpine-frontend', 'app', 'brand-variables.css');
  fs.writeFileSync(outputPath, css);
  console.log('✅ Generated CSS variables:', outputPath);
}

// Generate brand JSON for external tools
function generateBrandJSON() {
  const outputPath = path.join(__dirname, '..', 'brand-config.json');
  fs.writeFileSync(outputPath, JSON.stringify(AlpineBrand, null, 2));
  console.log('✅ Generated brand-config.json:', outputPath);
}

// Generate LaTeX color definitions
function generateLaTeXColors() {
  const latex = `
% Alpine Analytics Brand Colors for LaTeX
\\definecolor{alpine-black-pure}{RGB}{0,0,0}
\\definecolor{alpine-black-primary}{RGB}{10,10,15}
\\definecolor{alpine-black-secondary}{RGB}{15,15,26}
\\definecolor{alpine-black-tertiary}{RGB}{21,21,26}
\\definecolor{alpine-black-border}{RGB}{26,26,46}

\\definecolor{alpine-neon-cyan}{RGB}{24,224,255}
\\definecolor{alpine-neon-cyan-dark}{RGB}{0,184,212}
\\definecolor{alpine-neon-pink}{RGB}{254,28,128}
\\definecolor{alpine-neon-pink-dark}{RGB}{204,0,102}
\\definecolor{alpine-neon-purple}{RGB}{150,0,255}
\\definecolor{alpine-neon-purple-dark}{RGB}{83,32,249}
\\definecolor{alpine-neon-orange}{RGB}{255,95,1}
\\definecolor{alpine-neon-orange-dark}{RGB}{204,77,0}

\\definecolor{alpine-semantic-success}{RGB}{0,255,136}
\\definecolor{alpine-semantic-error}{RGB}{255,45,85}
\\definecolor{alpine-semantic-warning}{RGB}{255,95,1}
\\definecolor{alpine-semantic-info}{RGB}{24,224,255}

\\definecolor{alpine-text-primary}{RGB}{255,255,255}
\\definecolor{alpine-text-secondary}{RGB}{161,161,170}
\\definecolor{alpine-text-tertiary}{RGB}{113,113,122}
\\definecolor{alpine-text-inverse}{RGB}{0,0,0}
`;
  
  const outputPath = path.join(__dirname, 'alpine-brand-colors.tex');
  fs.writeFileSync(outputPath, latex);
  console.log('✅ Generated LaTeX colors:', outputPath);
}

// Main
console.log('🎨 Generating Alpine Analytics brand assets...\n');
generateCSSVariables();
generateBrandJSON();
generateLaTeXColors();
console.log('\n✅ Brand asset generation complete!');

