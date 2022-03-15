/**
 * Extends repo root config, only put changes here that are scoped to this specific package
 * (if you already are - evaluate whether you really need package scoped linting rules)
 */

/** @type {import("eslint").Linter.Config} */
const config = {
  env: {
    browser: true
  },
  overrides: [
    {
      files: ['render_page/**/*.js'],
      parserOptions: {
        sourceType: 'module'
      }
    }
  ]
}

module.exports = config
