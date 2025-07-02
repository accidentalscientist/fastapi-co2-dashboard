const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface DashboardStats {
  total_countries: number;
  latest_year: number;
  total_co2_emissions: number;
  avg_renewable_percentage: number;
  top_performers: { country: string; co2_per_capita: number }[];
  worst_performers: { country: string; co2_per_capita: number }[];
  last_updated: string;
}

export interface ChartData {
  type: string;
  title: string;
  data: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
      borderColor?: string;
      backgroundColor?: string;
      fill?: boolean;
    }>;
  };
  last_updated: string;
}

export interface ComparisonData {
  type: string;
  title: string;
  data: Array<{
    country: string;
    year1_value: number;
    year2_value: number;
    change: number;
    percent_change: number;
  }>;
  years: number[];
  last_updated: string;
}

export interface HealthStatus {
  status: string;
  database_connected: boolean;
  last_data_update: string | null;
  scheduler_running: boolean;
  total_records: number;
  uptime: string;
}

export interface LastUpdateInfo {
  last_updated: string | null;
  seconds_ago: number | null;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}/api/v1${endpoint}`);
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
  }

  async getDashboardStats(): Promise<DashboardStats> {
    return this.request<DashboardStats>('/dashboard/stats');
  }

  async getCO2TimeSeries(params?: {
    countries?: string[];
    start_year?: number;
    end_year?: number;
  }): Promise<ChartData> {
    const searchParams = new URLSearchParams();
    
    if (params?.countries) {
      params.countries.forEach(country => searchParams.append('countries', country));
    }
    if (params?.start_year) {
      searchParams.append('start_year', params.start_year.toString());
    }
    if (params?.end_year) {
      searchParams.append('end_year', params.end_year.toString());
    }

    const queryString = searchParams.toString();
    const endpoint = `/dashboard/co2-timeseries${queryString ? `?${queryString}` : ''}`;
    
    return this.request<ChartData>(endpoint);
  }

  async getRenewableEnergyData(params?: {
    year?: number;
    limit?: number;
  }): Promise<ChartData> {
    const searchParams = new URLSearchParams();
    
    if (params?.year) {
      searchParams.append('year', params.year.toString());
    }
    if (params?.limit) {
      searchParams.append('limit', params.limit.toString());
    }

    const queryString = searchParams.toString();
    const endpoint = `/dashboard/renewable-energy${queryString ? `?${queryString}` : ''}`;
    
    return this.request<ChartData>(endpoint);
  }

  async getEmissionsComparison(params?: {
    compare_years?: number[];
    limit?: number;
  }): Promise<ComparisonData> {
    const searchParams = new URLSearchParams();
    
    if (params?.compare_years) {
      params.compare_years.forEach(year => searchParams.append('compare_years', year.toString()));
    }
    if (params?.limit) {
      searchParams.append('limit', params.limit.toString());
    }

    const queryString = searchParams.toString();
    const endpoint = `/dashboard/emissions-comparison${queryString ? `?${queryString}` : ''}`;
    
    return this.request<ComparisonData>(endpoint);
  }

  async getCountries(): Promise<{ countries: string[] }> {
    return this.request<{ countries: string[] }>('/countries');
  }
}

export const apiClient = new ApiClient();