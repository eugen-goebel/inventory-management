// ESLint configuration.
//
// `npm run lint` has been in package.json since the project started, and all
// the plugins below sit in devDependencies, but the config file itself was
// never committed. The script therefore aborted with "ESLint couldn't find an
// eslint.config.* file" and no CI job called it, so nobody noticed.
//
// Flat config, which is the only format ESLint 9+ reads.
import js from "@eslint/js";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    // Build output and dependencies are not ours to lint.
    ignores: ["dist", "node_modules", "coverage"],
  },
  {
    files: ["**/*.{ts,tsx}"],
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],
      // Downgraded to a warning on purpose, not silenced.
      //
      // Five pages follow the same shape: a useCallback that sets a loading
      // flag and fetches, plus a useEffect that calls it. The rule is right
      // that this causes an extra render pass, but fixing it means reworking
      // how every page loads its data. That is a change to behaviour and
      // belongs in its own pull request with its own testing, not in the one
      // that makes the linter run at all.
      //
      // Left visible so the count cannot quietly grow.
      "react-hooks/set-state-in-effect": "warn",
    },
  },
  {
    // Vitest tests run in jsdom and use the globals injected by the test
    // setup, so the browser-only global list is not enough here.
    files: ["**/*.test.{ts,tsx}", "src/test/**/*.{ts,tsx}"],
    languageOptions: {
      globals: { ...globals.browser, ...globals.node },
    },
  },
);
