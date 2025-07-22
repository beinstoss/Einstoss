import api from './api';

export const parametersService = {
  // Get all parameters
  getParameters: async () => {
    const response = await api.get('/parameters');
    return response.data;
  },

  // Get parameter suggestions for autocomplete
  getAutocomplete: async (searchTerm = '') => {
    const response = await api.get(`/parameters/autocomplete?search=${encodeURIComponent(searchTerm)}`);
    return response.data;
  },

  // Validate parameters in text
  validateParameters: async (text) => {
    const response = await api.post('/parameters/validate', { text });
    return response.data;
  }
};