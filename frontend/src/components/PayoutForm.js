import React, { useState } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

function PayoutForm({ merchantId, onSuccess }) {
  const [amountRupees, setAmountRupees] = useState('');
  const [bankAccountId, setBankAccountId] = useState('ACC001');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const API_URL = 'http://localhost:8000/api/v1';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    setLoading(true);

    try {
      const amountPaise = Math.round(parseFloat(amountRupees) * 100);
      if (amountPaise <= 0) {
        setError('Amount must be greater than 0');
        setLoading(false);
        return;
      }

      const idempotencyKey = uuidv4();

      const response = await axios.post(
        `${API_URL}/payouts/`,
        {
          merchant_id: merchantId,
          amount_paise: amountPaise,
          bank_account_id: bankAccountId,
        },
        {
          headers: {
            'Idempotency-Key': idempotencyKey,
          },
        }
      );

      setSuccess(true);
      setAmountRupees('');
      onSuccess();
    } catch (err) {
      if (err.response?.status === 409) {
        setError('Insufficient funds');
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Failed to create payout');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mb-8 p-6 bg-white border border-gray-200 rounded-lg shadow">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Request Payout</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Amount (₹)
          </label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={amountRupees}
            onChange={(e) => setAmountRupees(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="100.50"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Bank Account
          </label>
          <select
            value={bankAccountId}
            onChange={(e) => setBankAccountId(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="ACC001">ACC001</option>
            <option value="ACC002">ACC002</option>
          </select>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? 'Processing...' : 'Request Payout'}
        </button>
      </form>
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded">
          {error}
        </div>
      )}
      {success && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded">
          Payout requested successfully!
        </div>
      )}
    </div>
  );
}

export default PayoutForm;
