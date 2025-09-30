import React from 'react';

interface ReportControlsProps {
  loading: boolean;
  onFetchReport: () => void;
  username?: string;
  onLogout: () => void;
}

export const ReportControls: React.FC<ReportControlsProps> = ({
  loading,
  onFetchReport,
  username,
  onLogout,
}) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold mb-2">Получить отчет</h2>
          <p className="text-gray-600">Собрать последние данные по телеметрии</p>
        </div>
        <div className="flex items-center space-x-4">
          {username && (
            <span className="text-sm text-gray-600">
              {username}
            </span>
          )}
          <button
            onClick={onLogout}
            className="px-4 py-2 text-sm bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            Выход
          </button>
          <button
            onClick={onFetchReport}
            disabled={loading}
            className={`px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors ${
              loading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {loading ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Загрузка...
              </span>
            ) : (
              'Показать отчет'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};