import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  FolderOpen, 
  FileText, 
  MessageSquare, 
  CheckCircle, 
  Clock, 
  TrendingUp,
  Bot,
  Users,
  Calendar,
  ArrowRight
} from 'lucide-react';
import { apiClient } from '../lib/api.jsx';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export default function Dashboard() {
  const [stats, setStats] = useState({
    projects: { total: 0, active: 0, completed: 0 },
    documents: { total: 0, processed: 0, pending: 0 },
    questions: { total: 0, answered: 0, pending: 0 },
    responses: { total: 0, approved: 0, draft: 0 }
  });
  
  const [recentProjects, setRecentProjects] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Carregar projetos recentes
      const projectsResponse = await apiClient.getProjects({ 
        limit: 5, 
        sort: 'created_at:desc' 
      });
      setRecentProjects(projectsResponse.data || []);

      // Simular estatísticas (em produção, viria do backend)
      setStats({
        projects: { total: 12, active: 8, completed: 4 },
        documents: { total: 45, processed: 38, pending: 7 },
        questions: { total: 234, answered: 189, pending: 45 },
        responses: { total: 189, approved: 156, draft: 33 }
      });

      // Simular atividade recente
      setRecentActivity([
        {
          id: 1,
          type: 'response_generated',
          message: 'Resposta gerada para pergunta Q1.2',
          project: 'RFP Modernização TI',
          timestamp: new Date(Date.now() - 1000 * 60 * 30)
        },
        {
          id: 2,
          type: 'document_uploaded',
          message: 'Documento RFP_TechCorp.pdf carregado',
          project: 'Proposta TechCorp',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2)
        },
        {
          id: 3,
          type: 'response_approved',
          message: '5 respostas aprovadas',
          project: 'RFP Infraestrutura Cloud',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4)
        }
      ]);

    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const chartData = [
    { name: 'Jan', respostas: 45, aprovadas: 38 },
    { name: 'Fev', respostas: 52, aprovadas: 44 },
    { name: 'Mar', respostas: 61, aprovadas: 55 },
    { name: 'Abr', respostas: 48, aprovadas: 41 },
    { name: 'Mai', respostas: 67, aprovadas: 59 },
    { name: 'Jun', respostas: 73, aprovadas: 68 }
  ];

  const pieData = [
    { name: 'Aprovadas', value: stats.responses.approved },
    { name: 'Rascunho', value: stats.responses.draft },
    { name: 'Em Revisão', value: 12 },
    { name: 'Rejeitadas', value: 8 }
  ];

  const getActivityIcon = (type) => {
    switch (type) {
      case 'response_generated': return <Bot className="h-4 w-4 text-blue-500" />;
      case 'document_uploaded': return <FileText className="h-4 w-4 text-green-500" />;
      case 'response_approved': return <CheckCircle className="h-4 w-4 text-green-500" />;
      default: return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Cabeçalho */}
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Visão geral do sistema de automação de RFPs
        </p>
      </div>

      {/* Cards de Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Projetos Ativos</CardTitle>
            <FolderOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.projects.active}</div>
            <p className="text-xs text-muted-foreground">
              de {stats.projects.total} projetos totais
            </p>
            <Progress 
              value={(stats.projects.active / stats.projects.total) * 100} 
              className="mt-2"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Documentos Processados</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.documents.processed}</div>
            <p className="text-xs text-muted-foreground">
              {stats.documents.pending} pendentes
            </p>
            <Progress 
              value={(stats.documents.processed / stats.documents.total) * 100} 
              className="mt-2"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Perguntas Respondidas</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.questions.answered}</div>
            <p className="text-xs text-muted-foreground">
              {stats.questions.pending} pendentes
            </p>
            <Progress 
              value={(stats.questions.answered / stats.questions.total) * 100} 
              className="mt-2"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Taxa de Aprovação</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round((stats.responses.approved / stats.responses.total) * 100)}%
            </div>
            <p className="text-xs text-muted-foreground">
              {stats.responses.approved} de {stats.responses.total} respostas
            </p>
            <Progress 
              value={(stats.responses.approved / stats.responses.total) * 100} 
              className="mt-2"
            />
          </CardContent>
        </Card>
      </div>

      {/* Gráficos e Listas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico de Respostas por Mês */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="h-5 w-5 mr-2" />
              Respostas Geradas por Mês
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="respostas" fill="#8884d8" name="Total" />
                <Bar dataKey="aprovadas" fill="#82ca9d" name="Aprovadas" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Gráfico de Status das Respostas */}
        <Card>
          <CardHeader>
            <CardTitle>Status das Respostas</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Projetos Recentes e Atividade */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Projetos Recentes */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Projetos Recentes</CardTitle>
            <Button variant="outline" size="sm" asChild>
              <a href="/projects">
                Ver Todos
                <ArrowRight className="h-4 w-4 ml-2" />
              </a>
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentProjects.map((project) => (
                <div key={project.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex-1">
                    <h4 className="font-medium">{project.name}</h4>
                    <p className="text-sm text-muted-foreground">
                      {project.client_name}
                    </p>
                    <div className="flex items-center space-x-2 mt-1">
                      <Badge variant={project.status === 'active' ? 'default' : 'secondary'}>
                        {project.status}
                      </Badge>
                      {project.submission_deadline && (
                        <div className="flex items-center text-xs text-muted-foreground">
                          <Calendar className="h-3 w-3 mr-1" />
                          {new Date(project.submission_deadline).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" asChild>
                    <a href={`/projects/${project.id}`}>
                      <ArrowRight className="h-4 w-4" />
                    </a>
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Atividade Recente */}
        <Card>
          <CardHeader>
            <CardTitle>Atividade Recente</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start space-x-3">
                  <div className="p-2 rounded-full bg-muted">
                    {getActivityIcon(activity.type)}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.message}</p>
                    <p className="text-xs text-muted-foreground">
                      {activity.project}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {activity.timestamp.toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Ações Rápidas */}
      <Card>
        <CardHeader>
          <CardTitle>Ações Rápidas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button asChild className="h-20 flex-col">
              <a href="/projects/new">
                <FolderOpen className="h-6 w-6 mb-2" />
                Novo Projeto
              </a>
            </Button>
            <Button asChild variant="outline" className="h-20 flex-col">
              <a href="/chat">
                <Bot className="h-6 w-6 mb-2" />
                Chat IA
              </a>
            </Button>
            <Button asChild variant="outline" className="h-20 flex-col">
              <a href="/knowledge">
                <FileText className="h-6 w-6 mb-2" />
                Base de Conhecimento
              </a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

