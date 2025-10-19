import { useState } from 'react';
import styled from 'styled-components';
import FileUpload from './components/FileUpload';
import TransactionTable from './components/TransactionTable';
import { ParseResponse } from './types/transaction';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;

  @media (max-width: 768px) {
    padding: 12px;
  }
`;

const Header = styled.header`
  text-align: center;
  color: white;
  margin-bottom: 40px;

  h1 {
    font-size: 36px;
    margin: 0 0 12px 0;
    font-weight: 700;

    @media (max-width: 768px) {
      font-size: 28px;
    }
  }

  p {
    font-size: 16px;
    margin: 0;
    opacity: 0.9;

    @media (max-width: 768px) {
      font-size: 14px;
    }
  }
`;

const Main = styled.main`
  max-width: 1200px;
  margin: 0 auto;
`;

const Footer = styled.footer`
  text-align: center;
  color: white;
  margin-top: 40px;
  opacity: 0.8;
  font-size: 14px;
`;

function App() {
  const [parsedData, setParsedData] = useState<ParseResponse | null>(null);

  // API URL - can be configured via environment variable
  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleParsed = (data: ParseResponse) => {
    setParsedData(data);
  };

  return (
    <AppContainer>
      <Header>
        <h1>Trade Republic Transaction Parser</h1>
        <p>Upload your PDF bank statement to extract and analyze transactions</p>
      </Header>

      <Main>
        <FileUpload onParsed={handleParsed} apiUrl={apiUrl} />
        {parsedData && <TransactionTable data={parsedData} />}
      </Main>

      <Footer>
        <p>Powered by AWS Bedrock (Claude) • Built with React & Python</p>
      </Footer>
    </AppContainer>
  );
}

export default App;
