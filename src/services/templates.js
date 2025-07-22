import api from './api';

export const templatesService = {
  // Get templates for application
  getTemplates: async (applicationName) => {
    const response = await api.get(`/templates?application=${applicationName}`);
    return response.data;
  },

  // Create new template
  createTemplate: async (applicationName, templateData) => {
    const response = await api.post(`/templates`, {
      ...templateData,
      applicationName
    });
    return response.data;
  },

  // Update template
  updateTemplate: async (applicationName, templateId, templateData) => {
    const response = await api.put(`/templates/${templateId}`, {
      ...templateData,
      applicationName
    });
    return response.data;
  },

  // Delete template
  deleteTemplate: async (templateId) => {
    const response = await api.delete(`/templates/${templateId}`);
    return response.data;
  }
};