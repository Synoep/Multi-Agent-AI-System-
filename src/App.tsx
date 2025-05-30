import React, { useState } from 'react';
import { Upload, Mail, FileJson, FileCheck, FileText } from 'lucide-react';

function App() {
  const [input, setInput] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const processInput = async () => {
    setLoading(true);
    try {
      // In a real implementation, this would call your Python backend
      const classification = {
        format: input.startsWith('{') ? 'json' : selectedFile?.type === 'application/pdf' ? 'pdf' : 'email',
        intent: input.toLowerCase().includes('quote') ? 'rfq' : 'inquiry'
      };

      let processedResult;
      if (classification.format === 'json') {
        processedResult = JSON.parse(input);
      } else if (classification.format === 'pdf' && selectedFile) {
        // Process PDF file
        processedResult = {
          filename: selectedFile.name,
          size: selectedFile.size,
          type: selectedFile.type
        };
      } else {
        // Simple email processing
        const lines = input.split('\n');
        processedResult = {
          from: lines.find(l => l.startsWith('From:'))?.slice(5).trim(),
          subject: lines.find(l => l.startsWith('Subject:'))?.slice(8).trim(),
          body: lines.filter(l => !l.startsWith('From:') && !l.startsWith('To:') && !l.startsWith('Subject:')).join('\n')
        };
      }

      setResult({
        classification,
        processed: processedResult,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error processing input:', error);
      setResult({ error: 'Failed to process input' });
    }
    setLoading(false);
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setInput(''); // Clear text input when PDF is selected
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <FileCheck className="w-8 h-8 text-blue-600" />
            Multi-Agent AI System
          </h1>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Input (JSON, Email, or PDF)
            </label>
            <div className="space-y-4">
              <textarea
                className="w-full h-48 px-3 py-2 text-gray-700 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  setSelectedFile(null); // Clear file selection when text is entered
                }}
                placeholder="Paste your JSON or email content here..."
                disabled={!!selectedFile}
              />
              <div className="flex items-center gap-2">
                <span className="text-gray-700">Or upload a PDF:</span>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>
            </div>
          </div>

          <div className="flex gap-4 mb-6">
            <button
              onClick={() => setInput(JSON.stringify({
                customer: "Acme Corp",
                order_id: "ORD-12345",
                items: [
                  {"product": "Widget A", "quantity": 5, "price": 10.99},
                  {"product": "Widget B", "quantity": 3, "price": 15.99}
                ],
                total: 129.92
              }, null, 2))}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            >
              <FileJson className="w-4 h-4" />
              Load Sample JSON
            </button>
            <button
              onClick={() => setInput(`From: john.doe@example.com
To: sales@company.com
Subject: Request for Quotation - Office Supplies

Hello,

We are interested in purchasing office supplies for our new branch.
Could you please provide a quotation for the following items:

- 20 ergonomic chairs
- 10 height-adjustable desks
- 15 desk lamps

We would appreciate a response within the next week.

Best regards,
John Doe
Procurement Manager
Acme Corp`)}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            >
              <Mail className="w-4 h-4" />
              Load Sample Email
            </button>
            <button
              onClick={() => {
                // In a real app, this would load a sample PDF
                alert('Sample PDF loading would be implemented in a real application');
              }}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            >
              <FileText className="w-4 h-4" />
              Load Sample PDF
            </button>
          </div>

          <button
            onClick={processInput}
            disabled={loading || (!input.trim() && !selectedFile)}
            className="flex items-center gap-2 px-6 py-3 text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
          >
            <Upload className="w-5 h-5" />
            {loading ? 'Processing...' : 'Process Input'}
          </button>

          {result && (
            <div className="mt-8">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Processing Result</h2>
              <div className="bg-gray-50 rounded-lg p-4">
                <pre className="whitespace-pre-wrap text-sm text-gray-700">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;