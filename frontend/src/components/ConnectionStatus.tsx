
import { CheckCircle, XCircle, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ConnectionStatusProps {
  connection: string;
}

export const ConnectionStatus = ({ connection }: ConnectionStatusProps) => {
  const getStatus = (conn: string) => {
    if (conn === 'production-db') return { status: 'connected', text: 'Connected', color: 'text-green-600' };
    if (conn === 'staging-db') return { status: 'disconnected', text: 'Disconnected', color: 'text-red-600' };
    return { status: 'connecting', text: 'Connecting...', color: 'text-yellow-600' };
  };

  const { status, text, color } = getStatus(connection);

  const StatusIcon = () => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="h-4 w-4" />;
      case 'disconnected':
        return <XCircle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4 animate-pulse" />;
    }
  };

  return (
    <div className={cn("flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100", color)}>
      <StatusIcon />
      <span className="text-sm font-medium">{text}</span>
      <span className="text-xs text-slate-500">({connection})</span>
    </div>
  );
};
