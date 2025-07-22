import api from './api';

export const formFieldsService = {
  // Get global form field configuration (applies to all applications)
  getFormConfiguration: async (applicationName) => {
    const response = await api.get(`/form-fields/configuration?application=${applicationName}`);
    return response.data.configuration;
  },

  // Get options for specific field
  getFieldOptions: async (fieldName) => {
    const response = await api.get(`/form-fields/${fieldName}/options`);
    return response.data.options;
  },

  // Get configuration for a specific field
  getFieldConfiguration: async (fieldName) => {
    const response = await api.get(`/form-fields/${fieldName}`);
    return response.data.configuration;
  }
};