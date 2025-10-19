export interface Transaction {
  date: string;
  isin: string;
  product_name: string;
  quantity: string;
  amount_euros: string;
  transaction_type: 'BUY' | 'SELL' | 'DIVIDEND';
}

export interface AggregatedTransaction {
  isin: string;
  product_name: string;
  total_quantity: string;
  total_amount_euros: string;
  transaction_type: 'BUY' | 'SELL' | 'DIVIDEND';
  transaction_count: number;
}

export interface ParseResponse {
  transactions: Transaction[];
  aggregated?: AggregatedTransaction[];
  total_transactions: number;
  pdf_filename: string;
  parsed_at: string;
}
