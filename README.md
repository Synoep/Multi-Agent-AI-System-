# Multi-Agent AI System

A sophisticated system that processes various input formats (JSON, Email, PDF) using specialized agents while maintaining shared context through a memory system.

![Multi-Agent System Demo](https://images.pexels.com/photos/1181671/pexels-photo-1181671.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2)

## Features

- 🤖 **Multiple Specialized Agents**
  - Classifier Agent for input format and intent detection
  - JSON Agent for structured data processing
  - Email Agent for email content analysis
  - PDF Agent for document processing

- 🧠 **Shared Memory System**
  - Cross-agent context maintenance
  - Conversation tracking
  - Thread-based information storage

- 🎯 **Smart Classification**
  - Format detection (JSON/Email/PDF)
  - Intent recognition (RFQ, Invoice, Complaint, Regulation)
  - Intelligent routing to specialized agents

- 💼 **Business-Ready Processing**
  - CRM-style data extraction
  - Anomaly detection
  - Structured output formatting
  - PDF text and metadata extraction

## Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **PDF Processing**: PDF.js
- **Testing**: Vitest

## Prerequisites

- Node.js 18+ and npm
- Python 3.8+ (for backend features)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd multi-agent-ai-system
```

2. Install frontend dependencies:
```bash
npm install
```

3. Install Python dependencies (optional, for backend features):
```bash
pip install -r requirements.txt
```

## Running the Project

1. Start the development server:
```bash
npm run dev
```

2. Open your browser and navigate to the local server URL (typically http://localhost:5173)

3. Test the system:
   - Use the "Load Sample JSON" button to test JSON processing
   - Use the "Load Sample Email" button to test email processing
   - Upload a PDF file to test PDF processing
   - Or paste your own JSON/email content

## Testing

Run the test suite:
```bash
npm run test
```

For test coverage:
```bash
npm run coverage
```

## Project Structure

```
src/
├── agents/              # AI agents implementation
│   ├── classifier_agent.py
│   ├── json_agent.py
│   ├── email_agent.py
│   └── pdf_agent.py
├── memory/             # Shared memory system
│   └── memory_store.py
├── utils/              # Utility functions
│   ├── logger.py
│   └── file_utils.py
└── components/         # React components
    └── App.tsx
```

## Features in Detail

### Classifier Agent
- Determines input format (JSON/Email/PDF) and intent
- Routes to appropriate specialized agent
- Maintains classification history

### JSON Agent
- Processes structured JSON data
- Validates against predefined schemas
- Detects anomalies and missing fields

### Email Agent
- Extracts sender information and intent
- Determines message urgency
- Formats data for CRM systems

### PDF Agent
- Extracts text content and metadata
- Processes based on document type (Invoice/RFQ/Regulation)
- Handles different PDF formats and structures
- Extracts key information based on intent

### Shared Memory
- Maintains context across processing steps
- Stores metadata and extracted information
- Enables conversation tracking

## Processing Capabilities

### PDF Processing
- **Invoice Processing**
  - Extract invoice numbers and dates
  - Identify line items and amounts
  - Calculate totals and verify consistency

- **RFQ Processing**
  - Extract RFQ numbers and deadlines
  - Identify requested items and quantities
  - Process submission requirements

- **Regulation Processing**
  - Extract regulation IDs and effective dates
  - Identify key requirements and compliance points
  - Process regulatory guidelines

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with React and Vite
- Styled with Tailwind CSS
- Icons from Lucide React
- PDF processing with PDF.js