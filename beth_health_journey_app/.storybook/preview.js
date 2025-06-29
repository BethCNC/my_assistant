import '../styles/globals.css';

// Optional: Import your generated CSS variables
// import '../styles/tokens-variables.css';

export const parameters = {
  actions: { argTypesRegex: '^on[A-Z].*' },
  controls: {
    matchers: {
      color: /(background|color)$/i,
      date: /Date$/,
    },
  },
  layout: 'centered',
  // Default Figma design options that can be overridden per component
  design: {
    type: 'figma',
    // Replace with your default Figma file URL
    url: 'https://www.figma.com/file/LKQ4FJ4bTnCSjedbRpk931/Sample-File',
  },
}; 