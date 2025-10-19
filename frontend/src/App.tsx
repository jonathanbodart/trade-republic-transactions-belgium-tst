import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import TransactionTable from './components/TransactionTable';
import { ParseResponse } from './types/transaction';
import './App.css';

function App() {
  const [parsedData, setParsedData] = useState<ParseResponse | null>(null);

  // API URL - can be configured via environment variable
  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleParsed = (data: ParseResponse) => {
    setParsedData(data);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Trade Republic Transaction Parser</h1>
        <p>Upload your PDF bank statement to extract and analyze transactions</p>
      </header>

      <main className="App-main">
        <FileUpload onParsed={handleParsed} apiUrl={apiUrl} />
        {parsedData && <TransactionTable data={parsedData} />}
      </main>

      <footer className="App-footer">
        <p>Powered by AWS Bedrock (Claude) • Built with React & Python</p>
      </footer>
    </div>
  );
}

export default App;
