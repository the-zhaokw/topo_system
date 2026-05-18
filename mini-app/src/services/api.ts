import Taro from '@tarojs/taro';

const BASE_URL = 'http://localhost:5000/api';

interface RequestOptions {
  url: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  data?: any;
  header?: Record<string, string>;
}

interface Response<T = any> {
  success: boolean;
  data: T;
  message?: string;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T = any>(options: RequestOptions): Promise<Response<T>> {
    const { url, method = 'GET', data, header = {} } = options;

    try {
      const token = Taro.getStorageSync('token');
      if (token) {
        header['Authorization'] = `Bearer ${token}`;
      }

      const response = await Taro.request({
        url: `${this.baseUrl}${url}`,
        method,
        data,
        header: {
          'Content-Type': 'application/json',
          ...header
        }
      });

      if (response.statusCode === 200) {
        return response.data;
      } else {
        console.error(`[API] Request failed with status ${response.statusCode}:`, response.data);
        return {
          success: false,
          data: null as T,
          message: response.data?.message || 'Request failed'
        };
      }
    } catch (error) {
      console.error('[API] Request error:', error);
      return {
        success: false,
        data: null as T,
        message: 'Network error'
      };
    }
  }

  public get<T = any>(url: string, data?: any): Promise<Response<T>> {
    return this.request<T>({ url, method: 'GET', data });
  }

  public post<T = any>(url: string, data?: any): Promise<Response<T>> {
    return this.request<T>({ url, method: 'POST', data });
  }

  public put<T = any>(url: string, data?: any): Promise<Response<T>> {
    return this.request<T>({ url, method: 'PUT', data });
  }

  public delete<T = any>(url: string, data?: any): Promise<Response<T>> {
    return this.request<T>({ url, method: 'DELETE', data });
  }
}

export default new ApiService(BASE_URL);
