import React, { useState, useEffect } from 'react';
import axios from 'axios';
import BalanceCard from './components/BalanceCard';
import PayoutForm from './components/PayoutForm';
import LedgerTable from './components/LedgerTable';
import PayoutHistoryTable from './components/PayoutHistoryTable';
import './App.css';

function App() {
  const [merchants, setMerchants] = useState([]);
  const [selectedMerchantId, setSelectedMerchantId] = useState(null);
  const [balance, setBalance] = useState(null);
  const [ledgerEntries, setLedgerEntries] = useState([]);
  const [payoutHistory, setPayoutHistory] = useState([]);

  const API_URL = 'http://localhost:8000/api/v1';

  // Fetch merchants on mount
  useEffect(() => {
    fetchMerchants();
  }, []);

  const fetchMerchants = async () => {
    try {
      const response = await axios.get(`${API_URL}/merchants/`);
      setMerchants(response.data);
      if (response.data.length > 0) {
        setSelectedMerchantId(response.data[0].id);
      }
    } catch (error) {
      console.error('Failed to fetch merchants:', error);
    }
  };

  // Fetch balance and ledger when merchant changes
  useEffect(() => {
    if (selectedMerchantId) {
      fetchBalance();
      fetchLedger();
      fetchPayoutHistory();
    }
  }, [selectedMerchantId]);

  // Auto-refresh payout statuses every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (selectedMerchantId) {
        fetchPayoutHistory();
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [selectedMerchantId]);

  const fetchBalance = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/merchants/${selectedMerchantId}/balance/`
      );
      setBalance(response.data);
    } catch (error) {
      console.error('Failed to fetch balance:', error);
    }
  };

  const fetchLedger = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/merchants/${selectedMerchantId}/ledger/`
      );
      setLedgerEntries(response.data.results || []);
    } catch (error) {
      console.error('Failed to fetch ledger:', error);
    }
  };

  const fetchPayoutHistory = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/merchants/${selectedMerchantId}/payouts/`
      );
      setPayoutHistory(response.data.results || []);
    } catch (error) {
      console.error('Failed to fetch payout history:', error);
    }
  };

  const handlePayoutSuccess = () => {
    fetchBalance();
    fetchLedger();
    fetchPayoutHistory();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Playto Payout Engine</h1>

        {/* Merchant Selector */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Merchant
          </label>
          <select
            value={selectedMerchantId || ''}
            onChange={(e) => setSelectedMerchantId(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {merchants.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
              </option>
            ))}
          </select>
        </div>

        {/* Balance Card */}
        {balance && <BalanceCard balance={balance} />}

        {/* Payout Form */}
        <PayoutForm
          merchantId={selectedMerchantId}
          onSuccess={handlePayoutSuccess}
        />

        {/* Ledger Table */}
        <LedgerTable entries={ledgerEntries} />

        {/* Payout History Table */}
        <PayoutHistoryTable payouts={payoutHistory} />
      </div>
    </div>
  );
}

export default App;
