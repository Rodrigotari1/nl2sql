
import { useState } from 'react';
import { DatabaseSidebar } from '@/components/DatabaseSidebar';
import { QueryEditor } from '@/components/QueryEditor';
import { ResultsPanel } from '@/components/ResultsPanel';
import { ConnectionStatus } from '@/components/ConnectionStatus';
import { Plus, Database, Settings, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';

const Index = () => {
  const [activeConnection, setActiveConnection] = useState('production-db');
  const [selectedTable, setSelectedTable] = useState('users');
  const [query, setQuery] = useState('SELECT * FROM users LIMIT 10;');

  return (
    <div className="h-screen flex flex-col bg-slate-50">
      {/* Header */}
      <header className="h-14 bg-white border-b border-slate-200 flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Database className="h-6 w-6 text-blue-600" />
            <h1 className="text-xl font-semibold text-slate-800">Zenith</h1>
          </div>
          <ConnectionStatus connection={activeConnection} />
        </div>
        
        <div className="flex items-center gap-2">
          <Link to="/nl2sql">
            <Button variant="outline" size="sm" className="gap-2">
              <Sparkles className="h-4 w-4" />
              NL2SQL
            </Button>
          </Link>
          <Button variant="outline" size="sm" className="gap-2">
            <Plus className="h-4 w-4" />
            New Connection
          </Button>
          <Button variant="ghost" size="sm">
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <DatabaseSidebar 
          activeConnection={activeConnection}
          selectedTable={selectedTable}
          onTableSelect={setSelectedTable}
          onConnectionChange={setActiveConnection}
        />
        
        {/* Main Panel */}
        <div className="flex-1 flex flex-col">
          {/* Query Editor */}
          <div className="h-80 border-b border-slate-200">
            <QueryEditor query={query} onQueryChange={setQuery} />
          </div>
          
          {/* Results Panel */}
          <div className="flex-1">
            <ResultsPanel selectedTable={selectedTable} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
