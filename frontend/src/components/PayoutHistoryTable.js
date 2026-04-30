import React from 'react';

function PayoutHistoryTable({ payouts }) {
  const formatRupees = (paise) => {
    const rupees = paise / 100;
    return `₹${rupees.toLocaleString('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN');
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const truncateId = (id) => {
    return id.substring(0, 8) + '...';
  };

  return (
    <div className="mb-8 p-6 bg-white border border-gray-200 rounded-lg shadow">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Payout History</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-gray-700">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-4 py-3 text-left font-medium text-gray-900">ID</th>
              <th className="px-4 py-3 text-left font-medium text-gray-900">Amount</th>
              <th className="px-4 py-3 text-left font-medium text-gray-900">Status</th>
              <th className="px-4 py-3 text-left font-medium text-gray-900">Created</th>
              <th className="px-4 py-3 text-left font-medium text-gray-900">Updated</th>
            </tr>
          </thead>
          <tbody>
            {payouts.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-4 py-3 text-center text-gray-500">
                  No payouts yet
                </td>
              </tr>
            ) : (
              payouts.map((payout) => (
                <tr key={payout.id} className="border-b hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-xs">{truncateId(payout.id)}</td>
                  <td className="px-4 py-3 font-mono">{formatRupees(payout.amount_paise)}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${getStatusBadgeClass(payout.status)}`}>
                      {payout.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs">{formatDate(payout.created_at)}</td>
                  <td className="px-4 py-3 text-xs">{formatDate(payout.updated_at)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default PayoutHistoryTable;
