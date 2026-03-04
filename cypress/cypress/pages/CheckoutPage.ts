import { BasePage } from './BasePage';

const SELECTORS = {
  firstName:           '[data-test="firstName"]',
  lastName:            '[data-test="lastName"]',
  postalCode:          '[data-test="postalCode"]',
  continueButton:      '[data-test="continue"]',
  finishButton:        '[data-test="finish"]',
  cancelButton:        '[data-test="cancel"]',
  confirmationHeader:  '.complete-header',
  confirmationText:    '.complete-text',
  errorMessage:        '[data-test="error"]',
} as const;

export class CheckoutPage extends BasePage {
  openStepOne(): void {
    this.visit('/checkout-step-one.html');
  }

  fillInfo(firstName: string, lastName: string, postalCode: string): void {
    this.type(SELECTORS.firstName, firstName);
    this.type(SELECTORS.lastName, lastName);
    this.type(SELECTORS.postalCode, postalCode);
  }

  continueToStepTwo(): void {
    this.click(SELECTORS.continueButton);
  }

  finish(): void {
    this.click(SELECTORS.finishButton);
  }

  cancel(): void {
    this.click(SELECTORS.cancelButton);
  }

  getConfirmationMessage(): Cypress.Chainable<string> {
    return this.getText(SELECTORS.confirmationHeader);
  }

  assertOrderComplete(): void {
    cy.get(SELECTORS.confirmationHeader).should(
      'contain.text',
      'Thank you for your order!',
    );
  }

  assertErrorContains(text: string): void {
    cy.get(SELECTORS.errorMessage).should('contain.text', text);
  }
}
