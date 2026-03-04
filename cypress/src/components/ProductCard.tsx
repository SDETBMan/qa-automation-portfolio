import React from 'react';

export interface ProductCardProps {
  name: string;
  price: number;
  onAddToCart: (name: string) => void;
}

/**
 * ProductCard — simple presentational component used by the Cypress
 * component test runner to demonstrate isolated React component testing.
 */
export const ProductCard: React.FC<ProductCardProps> = ({
  name,
  price,
  onAddToCart,
}) => {
  return (
    <div className="product-card" data-testid="product-card">
      <h3 className="product-name" data-testid="product-name">
        {name}
      </h3>
      <p className="product-price" data-testid="product-price">
        ${price.toFixed(2)}
      </p>
      <button
        className="add-to-cart-btn"
        data-testid="add-to-cart-btn"
        onClick={() => onAddToCart(name)}
      >
        Add to Cart
      </button>
    </div>
  );
};

export default ProductCard;
