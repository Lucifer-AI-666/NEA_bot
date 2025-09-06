module.exports = {
  extends: ['expo'],
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  rules: {
    // Add custom rules as needed
    '@typescript-eslint/no-unused-vars': 'warn',
  },
};