module.exports = ({ config }) => {
  // Add support for importing CSS
  config.module.rules.push({
    test: /\.css$/,
    use: [
      {
        loader: 'postcss-loader',
        options: {
          postcssOptions: {
            plugins: [
              require('tailwindcss'),
              require('autoprefixer'),
            ],
          },
        },
      },
    ],
    include: /\.css$/,
  });

  return config;
}; 