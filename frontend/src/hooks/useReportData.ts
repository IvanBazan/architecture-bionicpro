import { useState } from 'react';
import { useKeycloak } from '@react-keycloak/web';
import { ApiResponse, ReportState } from '../components/ReportPage/types';

export const useReportData = () => {
  const { keycloak } = useKeycloak();
  const [state, setState] = useState<ReportState>({
    data: null,
    loading: false,
    error: null,
  });

  const fetchReport = async () => {
    if (!keycloak?.token) {
      setState(prev => ({ ...prev, error: 'Not authenticated' }));
      return;
    }

    try {
      setState({ data: null, loading: true, error: null });

      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/reports`, {
        headers: {
          'Authorization': `Bearer ${keycloak.token}`
        }
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('Access denied: insufficient permissions');
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ApiResponse = await response.json();
      setState({ data, loading: false, error: null });
      
    } catch (err) {
      setState({
        data: null,
        loading: false,
        error: err instanceof Error ? err.message : 'An error occurred'
      });
    }
  };

  const clearError = () => {
    setState(prev => ({ ...prev, error: null }));
  };

  return {
    ...state,
    fetchReport,
    clearError,
  };
};