
import { useState } from 'react';
import { ChevronDown, ChevronRight, Database, Table, Key, Hash } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DatabaseSidebarProps {
  activeConnection: string;
  selectedTable: string;
  onTableSelect: (table: string) => void;
  onConnectionChange: (connection: string) => void;
}

export const DatabaseSidebar = ({ 
  activeConnection, 
  selectedTable, 
  onTableSelect,
  onConnectionChange 
}: DatabaseSidebarProps) => {
  const [expandedDatabases, setExpandedDatabases] = useState<Set<string>>(new Set(['production-db']));
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set(['users', 'orders']));

  const connections = [
    {
      name: 'production-db',
      type: 'PostgreSQL',
      status: 'connected',
      databases: [{
        name: 'ecommerce',
        tables: [
          { name: 'users', type: 'table', rows: 15420 },
          { name: 'orders', type: 'table', rows: 8932 },
          { name: 'products', type: 'table', rows: 2341 },
          { name: 'categories', type: 'table', rows: 45 },
          { name: 'user_sessions', type: 'view', rows: 0 }
        ]
      }]
    },
    {
      name: 'staging-db',
      type: 'PostgreSQL',
      status: 'disconnected',
      databases: []
    }
  ];

  const toggleDatabase = (dbName: string) => {
    const newExpanded = new Set(expandedDatabases);
    if (newExpanded.has(dbName)) {
      newExpanded.delete(dbName);
    } else {
      newExpanded.add(dbName);
    }
    setExpandedDatabases(newExpanded);
  };

  const toggleTable = (tableName: string) => {
    const newExpanded = new Set(expandedTables);
    if (newExpanded.has(tableName)) {
      newExpanded.delete(tableName);
    } else {
      newExpanded.add(tableName);
    }
    setExpandedTables(newExpanded);
  };

  return (
    <div className="w-80 bg-white border-r border-slate-200 flex flex-col">
      <div className="p-4 border-b border-slate-200">
        <h2 className="text-sm font-medium text-slate-600 uppercase tracking-wide">Connections</h2>
      </div>
      
      <div className="flex-1 overflow-auto">
        {connections.map((connection) => (
          <div key={connection.name} className="p-2">
            <div 
              className={cn(
                "flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors",
                activeConnection === connection.name 
                  ? "bg-blue-50 text-blue-700" 
                  : "hover:bg-slate-50"
              )}
              onClick={() => onConnectionChange(connection.name)}
            >
              <div className={cn(
                "w-2 h-2 rounded-full",
                connection.status === 'connected' ? "bg-green-500" : "bg-slate-400"
              )} />
              <Database className="h-4 w-4" />
              <div className="flex-1">
                <div className="text-sm font-medium">{connection.name}</div>
                <div className="text-xs text-slate-500">{connection.type}</div>
              </div>
              {expandedDatabases.has(connection.name) ? 
                <ChevronDown className="h-4 w-4" /> : 
                <ChevronRight className="h-4 w-4" />
              }
            </div>
            
            {expandedDatabases.has(connection.name) && connection.databases.map((db) => (
              <div key={db.name} className="ml-4 mt-2">
                <div 
                  className="flex items-center gap-2 p-2 rounded cursor-pointer hover:bg-slate-50"
                  onClick={() => toggleDatabase(db.name)}
                >
                  <Database className="h-4 w-4 text-slate-400" />
                  <span className="text-sm">{db.name}</span>
                </div>
                
                <div className="ml-6 mt-1 space-y-1">
                  {db.tables.map((table) => (
                    <div key={table.name}>
                      <div 
                        className={cn(
                          "flex items-center gap-2 p-2 rounded cursor-pointer transition-colors",
                          selectedTable === table.name 
                            ? "bg-blue-100 text-blue-700" 
                            : "hover:bg-slate-50"
                        )}
                        onClick={() => onTableSelect(table.name)}
                      >
                        <Table className="h-4 w-4 text-slate-400" />
                        <span className="text-sm flex-1">{table.name}</span>
                        <span className="text-xs text-slate-400">
                          {table.type === 'view' ? 'view' : `${table.rows.toLocaleString()}`}
                        </span>
                      </div>
                      
                      {expandedTables.has(table.name) && selectedTable === table.name && (
                        <div className="ml-6 space-y-1">
                          <div className="flex items-center gap-2 p-1 text-xs text-slate-500">
                            <Key className="h-3 w-3" />
                            <span>id (Primary Key)</span>
                          </div>
                          <div className="flex items-center gap-2 p-1 text-xs text-slate-500">
                            <Hash className="h-3 w-3" />
                            <span>email</span>
                          </div>
                          <div className="flex items-center gap-2 p-1 text-xs text-slate-500">
                            <Hash className="h-3 w-3" />
                            <span>created_at</span>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};
