import React from 'react';

function LedgerTable({ entries }) {
  const formatRupees = (paise) => {
    const rupees = paise / 100;
    return `₹${rupees.toLocaleString('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN') +
      ' ' +
      new Date(dateString).toLocaleTimeString('en-IN');
  };

  const getBadgeClass = (type) => {
    return type === 'credit'
      ? 'bg-green-100 text-green-800'
      : 'bg-red-100 text-red-800';
  };

  return (
    <div className="mb-8 p-6 bg-white border border-gray-200 rounded-lg shadow">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Ledger</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-gray-700">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-4 py-3 text-left font-medium text-gray-900">Date</th>
              <th className="px-4 py-3 text-left font-medium text-gray-900">Type</th>
              <th className="px-4 py-3 text-left font-medium text-gray-900">Description</th>
              <th className="px-4 py-3 text-right font-medium text-gray-900">Amount</th>
            </tr>
          </thead>
          <tbody>
            {entries.length === 0 ? (
              <tr>
                <td colSpan="4" className="px-4 py-3 text-center text-gray-500">
                  No entries yet
                </td>
              </tr>
            ) : (
              entries.map((entry) => (
                <tr key={entry.id} className="border-b hover:bg-gray-50">
                  <td className="px-4 py-3">{formatDate(entry.created_at)}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${getBadgeClass(entry.entry_type)}`}>
                      {entry.entry_type.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-4 py-3">{entry.description}</td>
                  <td className="px-4 py-3 text-right font-mono">
                    {formatRupees(entry.amount_paise)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default LedgerTable;
