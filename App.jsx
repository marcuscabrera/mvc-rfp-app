import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth.jsx';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import ChatInterface from './components/ChatInterface';
import LoginPage from './components/LoginPage';
import { Loader2 } from 'lucide-react';
import './App.css';

// Componente de proteção de rotas
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }
  
  return isAuthenticated ? children : <Navigate to="/login" />;
}

// Componente principal da aplicação
function AppContent() {
  const { isAuthenticated, loading } = useAuth();
  const [currentPath, setCurrentPath] = useState('/');

  useEffect(() => {
    setCurrentPath(window.location.pathname);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route 
          path="/login" 
          element={
            isAuthenticated ? <Navigate to="/" /> : <LoginPage />
          } 
        />
        
        <Route path="/*" element={
          <ProtectedRoute>
            <Layout currentPath={currentPath}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/projects" element={<ProjectsPage />} />
                <Route path="/documents" element={<DocumentsPage />} />
                <Route path="/chat" element={<ChatPage />} />
                <Route path="/knowledge" element={<KnowledgePage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        } />
      </Routes>
    </Router>
  );
}

// Páginas placeholder
function ProjectsPage() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Projetos</h1>
      <p className="text-muted-foreground">Gerenciamento de projetos RFP em desenvolvimento...</p>
    </div>
  );
}

function DocumentsPage() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Documentos</h1>
      <p className="text-muted-foreground">Gerenciamento de documentos em desenvolvimento...</p>
    </div>
  );
}

function ChatPage() {
  const [questions] = useState([
    {
      id: '1',
      question_text: 'Descreva a experiência da sua empresa em projetos de modernização de infraestrutura de TI.',
      question_number: 'Q1.1',
      section: 'Experiência Técnica',
      category: 'experience',
      required: true,
      current_response: {
        id: 'resp1',
        status: 'draft',
        word_count: 245
      }
    },
    {
      id: '2',
      question_text: 'Qual é a metodologia proposta para o gerenciamento do projeto?',
      question_number: 'Q2.1',
      section: 'Metodologia',
      category: 'technical',
      required: true,
      current_response: {
        id: 'resp2',
        status: 'approved',
        word_count: 189
      }
    },
    {
      id: '3',
      question_text: 'Apresente o cronograma detalhado das atividades do projeto.',
      question_number: 'Q3.1',
      section: 'Cronograma',
      category: 'planning',
      required: true
    }
  ]);

  return (
    <div className="h-[calc(100vh-4rem)]">
      <ChatInterface projectId="demo-project" questions={questions} />
    </div>
  );
}

function KnowledgePage() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Base de Conhecimento</h1>
      <p className="text-muted-foreground">Base de conhecimento em desenvolvimento...</p>
    </div>
  );
}

function SettingsPage() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Configurações</h1>
      <p className="text-muted-foreground">Configurações do sistema em desenvolvimento...</p>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
