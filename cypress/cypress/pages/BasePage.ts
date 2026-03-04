/**
 * BasePage — abstract helpers shared by all page objects.
 * Extend this class rather than using cy.* directly in tests.
 */
export abstract class BasePage {
  visit(path: string): void {
    cy.visit(path);
  }

  getText(selector: string): Cypress.Chainable<string> {
    return cy.get(selector).invoke('text');
  }

  isVisible(selector: string): Cypress.Chainable<boolean> {
    return cy.get(selector).then(($el) => $el.is(':visible'));
  }

  click(selector: string): void {
    cy.get(selector).click();
  }

  type(selector: string, value: string): void {
    cy.get(selector).type(value);
  }

  waitForUrl(urlFragment: string): void {
    cy.url().should('include', urlFragment);
  }

  getElement(selector: string): Cypress.Chainable<JQuery<HTMLElement>> {
    return cy.get(selector);
  }
}
