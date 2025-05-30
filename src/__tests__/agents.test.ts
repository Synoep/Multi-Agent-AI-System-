import { describe, test, expect } from 'vitest';
import { processInput } from '../agents/processor';

describe('Multi-Agent System', () => {
  test('processes JSON input correctly', () => {
    const jsonInput = JSON.stringify({
      customer: "Acme Corp",
      order_id: "ORD-12345",
      items: [
        {"product": "Widget A", "quantity": 5, "price": 10.99},
        {"product": "Widget B", "quantity": 3, "price": 15.99}
      ],
      total: 129.92
    });

    const result = processInput(jsonInput);
    expect(result.classification.format).toBe('json');
    expect(result.processed.customer).toBe('Acme Corp');
  });

  test('processes email input correctly', () => {
    const emailInput = `From: john.doe@example.com
To: sales@company.com
Subject: Request for Quotation - Office Supplies

Hello,

We are interested in purchasing office supplies.`;

    const result = processInput(emailInput);
    expect(result.classification.format).toBe('email');
    expect(result.processed.from).toBe('john.doe@example.com');
  });
});