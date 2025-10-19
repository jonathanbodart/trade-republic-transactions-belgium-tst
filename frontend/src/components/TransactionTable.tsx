import React from 'react';
import { Transaction, AggregatedTransaction, ParseResponse } from '../types/transaction';
import './TransactionTable.css';

interface TransactionTableProps {
  data: ParseResponse;
}

const TransactionTable: React.FC<TransactionTableProps> = ({ data }) => {
  const exportToJSON = () => {
    const dataStr = JSON.stringify(data.transactions, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    const exportFileDefaultName = `transactions_${new Date().toISOString().split('T')[0]}.json`;

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const exportToCSV = () => {
    const headers = ['Date', 'ISIN', 'Product Name', 'Quantity', 'Amount (EUR)', 'Type'];
    const rows = data.transactions.map(t => [
      t.date,
      t.isin,
      `"${t.product_name}"`,
      t.quantity,
      t.amount_euros,
      t.transaction_type
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    const dataUri = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent);
    const exportFileDefaultName = `transactions_${new Date().toISOString().split('T')[0]}.csv`;

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const getTypeClass = (type: string) => {
    switch (type) {
      case 'BUY':
        return 'type-buy';
      case 'SELL':
        return 'type-sell';
      case 'DIVIDEND':
        return 'type-dividend';
      default:
        return '';
    }
  };

  return (
    <div className="transaction-table-container">
      <div className="table-header">
        <div className="table-info">
          <h2>Parsed Transactions</h2>
          <div className="metadata">
            <span>File: <strong>{data.pdf_filename}</strong></span>
            <span>Total: <strong>{data.total_transactions}</strong> transactions</span>
            <span>Parsed: {new Date(data.parsed_at).toLocaleString()}</span>
          </div>
        </div>
        <div className="export-buttons">
          <button onClick={exportToJSON} className="export-btn">
            Export JSON
          </button>
          <button onClick={exportToCSV} className="export-btn">
            Export CSV
          </button>
        </div>
      </div>

      {data.aggregated && data.aggregated.length > 0 && (
        <div className="aggregated-section">
          <h3>Aggregated by ISIN</h3>
          <table className="transaction-table">
            <thead>
              <tr>
                <th>ISIN</th>
                <th>Product Name</th>
                <th className="align-right">Total Quantity</th>
                <th className="align-right">Total Amount (EUR)</th>
                <th>Type</th>
                <th className="align-center">Count</th>
              </tr>
            </thead>
            <tbody>
              {data.aggregated.map((txn, index) => (
                <tr key={index}>
                  <td className="isin">{txn.isin}</td>
                  <td className="product-name">{txn.product_name}</td>
                  <td className="align-right">{parseFloat(txn.total_quantity).toFixed(6)}</td>
                  <td className="align-right">€{parseFloat(txn.total_amount_euros).toFixed(2)}</td>
                  <td>
                    <span className={`type-badge ${getTypeClass(txn.transaction_type)}`}>
                      {txn.transaction_type}
                    </span>
                  </td>
                  <td className="align-center">{txn.transaction_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="transactions-section">
        <h3>All Transactions</h3>
        <table className="transaction-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>ISIN</th>
              <th>Product Name</th>
              <th className="align-right">Quantity</th>
              <th className="align-right">Amount (EUR)</th>
              <th>Type</th>
            </tr>
          </thead>
          <tbody>
            {data.transactions.map((txn, index) => (
              <tr key={index}>
                <td>{txn.date}</td>
                <td className="isin">{txn.isin}</td>
                <td className="product-name">{txn.product_name}</td>
                <td className="align-right">{parseFloat(txn.quantity).toFixed(6)}</td>
                <td className="align-right">€{parseFloat(txn.amount_euros).toFixed(2)}</td>
                <td>
                  <span className={`type-badge ${getTypeClass(txn.transaction_type)}`}>
                    {txn.transaction_type}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TransactionTable;
