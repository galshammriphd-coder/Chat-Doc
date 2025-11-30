import React from 'react';
import { AlertTriangle } from 'lucide-react';

const ErrorMessage = ({ message }) => {
    if (!message) return null;

    return (
        <div className="fixed top-4 right-4 max-w-md bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg shadow-lg flex items-start gap-3 z-50 animate-in slide-in-from-right">
            <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
                <h3 className="font-medium">Error</h3>
                <p className="text-sm mt-1">{message}</p>
            </div>
        </div>
    );
};

export default ErrorMessage;
