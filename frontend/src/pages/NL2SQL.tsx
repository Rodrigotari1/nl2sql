
import { useState } from 'react';
import { Database, Sparkles, Copy, Download, ChevronRight, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const NL2SQL = () => {
  const [connectionString, setConnectionString] = useState('');
  const [naturalQuery, setNaturalQuery] = useState('');
  const [generatedSQL, setGeneratedSQL] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);

  const suggestedQueries = [
    "Show me the top 10 users by order count",
    "What are the most popular product categories?",
    "Find users who haven't placed orders in the last 30 days",
    "Calculate total revenue by month for this year",
    "Show me customers with the highest lifetime value"
  ];

  const handleConnect = async () => {
    if (!connectionString.trim()) return;
    setIsConnected(true);
  };

  const handleGenerateSQL = async () => {
    if (!naturalQuery.trim()) return;
    
    setIsGenerating(true);
    // Simulate SQL generation
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Mock generated SQL based on query
    const mockSQL = `SELECT u.id, u.name, u.email, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name, u.email
ORDER BY order_count DESC
LIMIT 10;`;
    
    setGeneratedSQL(mockSQL);
    setIsGenerating(false);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute inset-0 bg-gradient-to-r from-white/5 to-transparent"></div>
        <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_50%,rgba(120,119,198,0.1),transparent_70%)]"></div>
      </div>
      
      <div className="relative z-10">
        {/* Header */}
        <header className="text-center py-16 px-4">
          <div className="inline-flex items-center gap-3 mb-6">
            <div className="p-3 bg-white/10 backdrop-blur-sm rounded-2xl">
              <Sparkles className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-6xl font-bold bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent">
              nl2sql
            </h1>
          </div>
          <p className="text-xl text-white/80 max-w-2xl mx-auto">
            Transform natural language into powerful SQL queries with AI precision
          </p>
        </header>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 pb-16">
          <div className="grid lg:grid-cols-2 gap-8 mb-8">
            {/* Database Connection */}
            <Card className="bg-white/10 backdrop-blur-lg border-white/20 text-white">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Database Connection
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">PostgreSQL Connection String</label>
                  <Input
                    value={connectionString}
                    onChange={(e) => setConnectionString(e.target.value)}
                    placeholder="postgresql://username:password@localhost:5432/database"
                    className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
                  />
                </div>
                <Button 
                  onClick={handleConnect}
                  disabled={!connectionString.trim() || isConnected}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 transition-all duration-300"
                >
                  {isConnected ? (
                    <>
                      <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                      Connected
                    </>
                  ) : (
                    'Connect Database'
                  )}
                </Button>
                
                {isConnected && (
                  <div className="mt-4 p-3 bg-green-500/20 border border-green-500/30 rounded-lg">
                    <p className="text-sm text-green-200">
                      ✓ Successfully connected to your database
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Natural Language Query */}
            <Card className="bg-white/10 backdrop-blur-lg border-white/20 text-white">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5" />
                  Natural Language Query
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Ask your question</label>
                  <Textarea
                    value={naturalQuery}
                    onChange={(e) => setNaturalQuery(e.target.value)}
                    placeholder="e.g., Show me the top 10 users by order count"
                    className="bg-white/10 border-white/20 text-white placeholder:text-white/50 min-h-[100px]"
                  />
                </div>
                
                <div>
                  <p className="text-sm font-medium mb-2">Suggested Questions:</p>
                  <div className="space-y-2">
                    {suggestedQueries.map((query, index) => (
                      <button
                        key={index}
                        onClick={() => setNaturalQuery(query)}
                        className="w-full text-left p-2 text-sm bg-white/5 hover:bg-white/10 rounded-lg transition-colors duration-200 flex items-center gap-2 group"
                      >
                        <ChevronRight className="h-4 w-4 text-white/60 group-hover:text-white transition-colors" />
                        {query}
                      </button>
                    ))}
                  </div>
                </div>
                
                <Button 
                  onClick={handleGenerateSQL}
                  disabled={!naturalQuery.trim() || !isConnected || isGenerating}
                  className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 transition-all duration-300"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Generating SQL...
                    </>
                  ) : (
                    'Generate SQL'
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Results Section */}
          {generatedSQL && (
            <Card className="bg-white/10 backdrop-blur-lg border-white/20 text-white">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Generated SQL Query</span>
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyToClipboard(generatedSQL)}
                      className="text-white hover:bg-white/10"
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-white hover:bg-white/10"
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-black/20 rounded-lg p-4 mb-4">
                  <pre className="text-sm font-mono text-green-300 whitespace-pre-wrap">
                    {generatedSQL}
                  </pre>
                </div>
                
                <Button 
                  onClick={() => setIsExecuting(!isExecuting)}
                  className="bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 transition-all duration-300"
                >
                  {isExecuting ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Executing...
                    </>
                  ) : (
                    'Execute Query'
                  )}
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default NL2SQL;
