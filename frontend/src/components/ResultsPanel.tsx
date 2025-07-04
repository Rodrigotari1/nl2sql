
import { useState } from 'react';
import { Download, Filter, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ResultsPanelProps {
  selectedTable: string;
}

export const ResultsPanel = ({ selectedTable }: ResultsPanelProps) => {
  const [isLoading, setIsLoading] = useState(false);

  // Mock data based on selected table
  const mockData = {
    users: [
      { id: 1, email: 'john.doe@company.com', name: 'John Doe', created_at: '2024-01-15', status: 'active' },
      { id: 2, email: 'jane.smith@company.com', name: 'Jane Smith', created_at: '2024-01-16', status: 'active' },
      { id: 3, email: 'bob.wilson@company.com', name: 'Bob Wilson', created_at: '2024-01-17', status: 'inactive' },
      { id: 4, email: 'alice.brown@company.com', name: 'Alice Brown', created_at: '2024-01-18', status: 'active' },
      { id: 5, email: 'charlie.davis@company.com', name: 'Charlie Davis', created_at: '2024-01-19', status: 'pending' }
    ],
    orders: [
      { id: 1001, user_id: 1, total: 129.99, status: 'shipped', created_at: '2024-01-20' },
      { id: 1002, user_id: 2, total: 79.50, status: 'processing', created_at: '2024-01-21' },
      { id: 1003, user_id: 3, total: 299.99, status: 'delivered', created_at: '2024-01-22' },
      { id: 1004, user_id: 1, total: 45.00, status: 'cancelled', created_at: '2024-01-23' }
    ],
    products: [
      { id: 1, name: 'Wireless Headphones', price: 99.99, category: 'Electronics', stock: 150 },
      { id: 2, name: 'Coffee Maker', price: 79.99, category: 'Appliances', stock: 50 },
      { id: 3, name: 'Notebook Set', price: 19.99, category: 'Office', stock: 200 }
    ]
  };

  const currentData = mockData[selectedTable as keyof typeof mockData] || mockData.users;
  const columns = currentData.length > 0 ? Object.keys(currentData[0]) : [];

  const refresh = async () => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsLoading(false);
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Results Header */}
      <div className="flex items-center justify-between p-3 border-b border-slate-200 bg-slate-50">
        <div className="flex items-center gap-4">
          <h3 className="font-medium text-slate-700">Results</h3>
          <span className="text-sm text-slate-500">
            {currentData.length} rows • Executed in 0.043s
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={refresh}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
          <Button variant="ghost" size="sm">
            <Filter className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Download className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      {/* Data Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full">
          <thead className="bg-slate-50 sticky top-0">
            <tr>
              {columns.map((column) => (
                <th key={column} className="text-left p-3 font-medium text-slate-700 border-b border-slate-200">
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentData.map((row, index) => (
              <tr 
                key={index} 
                className="hover:bg-slate-50 transition-colors border-b border-slate-100"
              >
                {columns.map((column) => (
                  <td key={column} className="p-3 text-sm text-slate-600">
                    <div className="max-w-xs truncate">
                      {typeof row[column as keyof typeof row] === 'object' 
                        ? JSON.stringify(row[column as keyof typeof row])
                        : String(row[column as keyof typeof row])
                      }
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* Pagination */}
      <div className="p-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-sm text-slate-600">
        <span>Showing 1-{currentData.length} of {currentData.length} results</span>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" disabled>Previous</Button>
          <span className="px-2">1</span>
          <Button variant="outline" size="sm" disabled>Next</Button>
        </div>
      </div>
    </div>
  );
};
