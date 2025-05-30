interface ProcessingResult {
  classification: {
    format: 'json' | 'email';
    intent: string;
  };
  processed: any;
  timestamp: string;
}

export function processInput(input: string): ProcessingResult {
  // Classify input
  const classification = {
    format: input.startsWith('{') ? 'json' : 'email',
    intent: input.toLowerCase().includes('quote') ? 'rfq' : 'inquiry'
  };

  // Process based on format
  let processed;
  if (classification.format === 'json') {
    processed = JSON.parse(input);
  } else {
    const lines = input.split('\n');
    processed = {
      from: lines.find(l => l.startsWith('From:'))?.slice(5).trim(),
      subject: lines.find(l => l.startsWith('Subject:'))?.slice(8).trim(),
      body: lines.filter(l => !l.startsWith('From:') && !l.startsWith('To:') && !l.startsWith('Subject:')).join('\n')
    };
  }

  return {
    classification,
    processed,
    timestamp: new Date().toISOString()
  };
}