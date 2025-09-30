import React from 'react';
import { useKeycloak } from '@react-keycloak/web';
import { useReportData } from '../../hooks/useReportData';
import { ReportControls } from './ReportControls';
import { UserInfoCard } from './UserInfoCard';
import { TelemetryTable } from './TelemetryTable';
import { ErrorDisplay } from './ErrorDisplay';

export const ReportPage: React.FC = () => {
  const { keycloak, initialized } = useKeycloak();
  const { data, loading, error, fetchReport, clearError } = useReportData();

  if (!initialized) {
    return <div className="flex items-center justify-center min-h-screen">Загрузка...</div>;
  }

  if (!keycloak.authenticated) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
        <div className="p-8 bg-white rounded-lg shadow-md text-center">
          <h1 className="text-2xl font-bold mb-4">Отчет по использованию</h1>
          <p className="mb-4 text-gray-600">Для получения отчета необходимо выполнить вход</p>
          <button
            onClick={() => keycloak.login()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Вход
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">Отчет по использованию</h1>
              <p className="text-gray-600 mt-2">Данные телеметрии вашего протеза</p>
            </div>
          </div>

          {/* Controls */}
          <ReportControls
            loading={loading}
            onFetchReport={fetchReport}
            username={keycloak.tokenParsed?.preferred_username}
            onLogout={() => keycloak.logout()}
          />

          {/* Error Display */}
          {error && <ErrorDisplay error={error} onClear={clearError} />}

          {/* Report Data */}
          {data && (
            <div className="space-y-6">
              <UserInfoCard user={data.user} />
              <TelemetryTable data={data.telemetry_data} count={data.count} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};