// Cliente da API para comunicação com o backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('access_token');
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
  }

  getAuthHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }
    
    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: this.getAuthHeaders(),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (response.status === 401) {
        // Token expirado, redirecionar para login
        this.setToken(null);
        window.location.href = '/login';
        return;
      }

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error?.message || 'Erro na requisição');
      }
      
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Métodos de autenticação
  async getCurrentUser() {
    return this.request('/auth/me');
  }

  async logout() {
    await this.request('/auth/logout', { method: 'POST' });
    this.setToken(null);
  }

  // Métodos de projetos
  async getProjects(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/projects${queryString ? `?${queryString}` : ''}`);
  }

  async getProject(id) {
    return this.request(`/projects/${id}`);
  }

  async createProject(data) {
    return this.request('/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateProject(id, data) {
    return this.request(`/projects/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // Métodos de documentos
  async uploadDocument(file, projectId, documentType = 'rfp') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);
    formData.append('document_type', documentType);

    return fetch(`${this.baseURL}/documents`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
      body: formData,
    }).then(response => {
      if (!response.ok) {
        throw new Error('Erro no upload');
      }
      return response.json();
    });
  }

  async getDocuments(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/documents${queryString ? `?${queryString}` : ''}`);
  }

  // Métodos de perguntas
  async getQuestions(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/questions${queryString ? `?${queryString}` : ''}`);
  }

  async extractQuestionsFromDocument(documentId, options = {}) {
    return this.request(`/questions/extract-from-document/${documentId}`, {
      method: 'POST',
      body: JSON.stringify(options),
    });
  }

  async updateQuestion(id, data) {
    return this.request(`/questions/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // Métodos de respostas
  async generateResponse(questionId, options = {}) {
    return this.request(`/responses/generate/${questionId}`, {
      method: 'POST',
      body: JSON.stringify(options),
    });
  }

  async updateResponse(id, data) {
    return this.request(`/responses/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async approveResponse(id, comments = '') {
    return this.request(`/responses/${id}/approve`, {
      method: 'POST',
      body: JSON.stringify({ comments }),
    });
  }

  async rejectResponse(id, comments = '') {
    return this.request(`/responses/${id}/reject`, {
      method: 'POST',
      body: JSON.stringify({ comments }),
    });
  }

  async getResponseVersions(questionId) {
    return this.request(`/responses/question/${questionId}/versions`);
  }

  // Métodos de base de conhecimento
  async searchKnowledgeBase(query, options = {}) {
    return this.request('/knowledge-base/search', {
      method: 'POST',
      body: JSON.stringify({ query, ...options }),
    });
  }

  async getKnowledgeBase(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/knowledge-base${queryString ? `?${queryString}` : ''}`);
  }

  // Métodos de organização
  async getCurrentOrganization() {
    return this.request('/organizations/current');
  }
}

export const apiClient = new ApiClient();
export default apiClient;

