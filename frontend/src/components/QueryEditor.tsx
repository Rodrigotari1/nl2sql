
import { useState } from 'react';
import { Play, Save, Download, Copy } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

interface QueryEditorProps {
  query: string;
  onQueryChange: (query: string) => void;
}

export const QueryEditor = ({ query, onQueryChange }: QueryEditorProps) => {
  const [isExecuting, setIsExecuting] = useState(false);

  const executeQuery = async () => {
    setIsExecuting(true);
    // Simulate query execution
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsExecuting(false);
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-3 border-b border-slate-200 bg-slate-50">
        <div className="flex items-center gap-2">
          <Button 
            onClick={executeQuery} 
            disabled={isExecuting}
            className="gap-2 bg-blue-600 hover:bg-blue-700"
            size="sm"
          >
            <Play className="h-4 w-4" />
            {isExecuting ? 'Executing...' : 'Run Query'}
          </Button>
          <Button variant="outline" size="sm" className="gap-2">
            <Save className="h-4 w-4" />
            Save
          </Button>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm">
            <Copy className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Download className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      {/* Editor */}
      <div className="flex-1 p-4">
        <Textarea
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          className="h-full font-mono text-sm resize-none border border-slate-200 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
          placeholder="Enter your SQL query here..."
          style={{
            fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
            lineHeight: '1.5'
          }}
        />
      </div>
      
      {/* Status bar */}
      <div className="px-4 py-2 bg-slate-50 border-t border-slate-200 text-xs text-slate-500 flex justify-between">
        <span>Line 1, Column 1</span>
        <span>PostgreSQL • UTF-8</span>
      </div>
    </div>
  );
};
