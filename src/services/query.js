import api from './api';

export const queryService = {
  // Query templates with filters
  queryTemplates: async (filters = [], sortBy = null, sortOrder = 'asc', page = 1, pageSize = 50) => {
    const response = await api.post('/query/templates', {
      filters,
      sort_by: sortBy,
      sort_order: sortOrder,
      page,
      page_size: pageSize
    });
    return response.data;
  },

  // Get query metadata
  getMetadata: async () => {
    const response = await api.get('/query/templates/metadata');
    return response.data;
  },

  // Get count only
  getCount: async (filters = []) => {
    const response = await api.get(`/query/templates/count?filters=${encodeURIComponent(JSON.stringify(filters))}`);
    return response.data;
  },

  // Export templates
  exportTemplates: async (filters = [], format = 'json') => {
    const response = await api.get(`/query/templates/export?format=${format}&filters=${encodeURIComponent(JSON.stringify(filters))}`, {
      responseType: format === 'json' ? 'json' : 'blob'
    });
    return response;
  }
};