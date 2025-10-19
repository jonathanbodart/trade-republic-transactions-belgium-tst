import React, { useState } from 'react';
import axios from 'axios';
import { ParseResponse } from '../types/transaction';
import './FileUpload.css';

interface FileUploadProps {
  onParsed: (data: ParseResponse) => void;
  apiUrl: string;
}

const FileUpload: React.FC<FileUploadProps> = ({ onParsed, apiUrl }) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [aggregate, setAggregate] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('aggregate', String(aggregate));

    try {
      const response = await axios.post<ParseResponse>(`${apiUrl}/parse`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      onParsed(response.data);
      setFile(null);
      // Reset file input
      const fileInput = document.getElementById('file-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to parse PDF';
      setError(errorMessage);
      console.error('Error uploading file:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="file-upload">
      <h2>Upload Trade Republic Statement</h2>

      <div className="upload-controls">
        <input
          id="file-input"
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          disabled={loading}
        />

        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={aggregate}
            onChange={(e) => setAggregate(e.target.checked)}
            disabled={loading}
          />
          Aggregate by ISIN
        </label>

        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className="upload-button"
        >
          {loading ? 'Parsing...' : 'Upload & Parse'}
        </button>
      </div>

      {file && (
        <div className="file-info">
          Selected file: <strong>{file.name}</strong> ({Math.round(file.size / 1024)} KB)
        </div>
      )}

      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}
    </div>
  );
};

export default FileUpload;
