// Global support file — imported automatically before every E2E spec.
import './commands';

// Allure reporting — generates rich HTML reports in CI
import '@shelex/cypress-allure-plugin';

// Accessibility testing — adds cy.injectAxe() and cy.checkA11y()
import 'cypress-axe';

// Lighthouse performance audits — adds cy.lighthouse() (Chrome only)
import '@cypress-audit/lighthouse/commands';
