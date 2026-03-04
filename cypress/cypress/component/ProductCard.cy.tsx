import React from 'react';
import { ProductCard } from '../../src/components/ProductCard';

describe('ProductCard component', () => {
  it('renders product name and price', () => {
    cy.mount(
      <ProductCard
        name="Sauce Labs Backpack"
        price={29.99}
        onAddToCart={cy.stub()}
      />,
    );

    cy.get('[data-testid="product-name"]').should(
      'have.text',
      'Sauce Labs Backpack',
    );
    cy.get('[data-testid="product-price"]').should('have.text', '$29.99');
  });

  it('calls onAddToCart callback when button is clicked', () => {
    const onAddToCart = cy.stub().as('addToCartStub');

    cy.mount(
      <ProductCard
        name="Sauce Labs Bike Light"
        price={9.99}
        onAddToCart={onAddToCart}
      />,
    );

    cy.get('[data-testid="add-to-cart-btn"]').click();
    cy.get('@addToCartStub').should(
      'have.been.calledOnceWith',
      'Sauce Labs Bike Light',
    );
  });

  it('renders correctly with a long product name', () => {
    const longName =
      'Sauce Labs Extra Long Product Name That Could Potentially Overflow The Card Layout In Some Designs';

    cy.mount(
      <ProductCard name={longName} price={99.99} onAddToCart={cy.stub()} />,
    );

    cy.get('[data-testid="product-card"]').should('be.visible');
    cy.get('[data-testid="product-name"]').should('have.text', longName);
  });

  it('displays formatted price with two decimal places', () => {
    cy.mount(
      <ProductCard name="Cheap Widget" price={7.9} onAddToCart={cy.stub()} />,
    );

    // 7.9 → "$7.90" (toFixed(2) in component)
    cy.get('[data-testid="product-price"]').should('have.text', '$7.90');
  });
});
