import React from 'react';

function BalanceCard({ balance }) {
  const formatRupees = (paise) => {
    const rupees = paise / 100;
    return `₹${rupees.toLocaleString('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  return (
    <div className="mb-8 p-6 bg-white border border-gray-200 rounded-lg shadow">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Balance Summary</h2>
      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 bg-blue-50 border border-blue-200 rounded">
          <p className="text-sm text-gray-600">Ledger Balance</p>
          <p className="text-2xl font-bold text-blue-600">
            {formatRupees(balance.ledger_balance)}
          </p>
        </div>
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-sm text-gray-600">Held Balance</p>
          <p className="text-2xl font-bold text-yellow-600">
            {formatRupees(balance.held_balance)}
          </p>
        </div>
        <div className="p-4 bg-green-50 border border-green-200 rounded">
          <p className="text-sm text-gray-600">Available Balance</p>
          <p className="text-2xl font-bold text-green-600">
            {formatRupees(balance.available_balance)}
          </p>
        </div>
      </div>
    </div>
  );
}

export default BalanceCard;
