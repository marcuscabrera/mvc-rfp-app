import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Bot, Shield, Users, Zap } from 'lucide-react';
import { useAuth } from '../hooks/useAuth.jsx';

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleAzureLogin = async () => {
    setLoading(true);
    setError('');

    try {
      // Simular login com Azure EntraID
      // Em produção, redirecionaria para o endpoint de autenticação
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Simular dados do usuário retornados pelo Azure
      const mockUserData = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        email: 'usuario@empresa.com',
        first_name: 'João',
        last_name: 'Silva',
        display_name: 'João Silva',
        organization: {
          id: 'org-123',
          name: 'Empresa Demo'
        }
      };

      const mockToken = 'mock-jwt-token-' + Date.now();
      
      login(mockToken, mockUserData);
      window.location.href = '/';
      
    } catch (err) {
      setError('Erro ao fazer login. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
        {/* Lado esquerdo - Informações */}
        <div className="space-y-6">
          <div className="flex items-center space-x-3">
            <Bot className="h-12 w-12 text-primary" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">RFP Automation</h1>
              <p className="text-lg text-gray-600">Sistema de Automação de Respostas</p>
            </div>
          </div>
          
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-gray-900">
              Automatize suas respostas a RFPs com IA
            </h2>
            <p className="text-gray-600 text-lg">
              Acelere o processo de resposta a RFPs com nossa plataforma inteligente 
              que extrai perguntas automaticamente e gera respostas personalizadas.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex items-center space-x-3 p-4 bg-white rounded-lg shadow-sm">
              <Zap className="h-8 w-8 text-yellow-500" />
              <div>
                <h3 className="font-semibold">Geração Automática</h3>
                <p className="text-sm text-gray-600">Respostas inteligentes com IA</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-4 bg-white rounded-lg shadow-sm">
              <Shield className="h-8 w-8 text-green-500" />
              <div>
                <h3 className="font-semibold">Seguro e Confiável</h3>
                <p className="text-sm text-gray-600">Autenticação Azure EntraID</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-4 bg-white rounded-lg shadow-sm">
              <Users className="h-8 w-8 text-blue-500" />
              <div>
                <h3 className="font-semibold">Colaborativo</h3>
                <p className="text-sm text-gray-600">Trabalhe em equipe</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-4 bg-white rounded-lg shadow-sm">
              <Bot className="h-8 w-8 text-purple-500" />
              <div>
                <h3 className="font-semibold">Chat Interativo</h3>
                <p className="text-sm text-gray-600">Interface conversacional</p>
              </div>
            </div>
          </div>
        </div>

        {/* Lado direito - Login */}
        <div className="flex justify-center">
          <Card className="w-full max-w-md">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl">Fazer Login</CardTitle>
              <p className="text-muted-foreground">
                Entre com sua conta corporativa
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              
              <Button 
                onClick={handleAzureLogin}
                disabled={loading}
                className="w-full h-12 text-lg"
                size="lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Conectando...
                  </>
                ) : (
                  <>
                    <Shield className="mr-2 h-5 w-5" />
                    Entrar com Azure EntraID
                  </>
                )}
              </Button>
              
              <div className="text-center text-sm text-muted-foreground">
                <p>
                  Ao fazer login, você concorda com nossos{' '}
                  <a href="#" className="underline">Termos de Uso</a>{' '}
                  e{' '}
                  <a href="#" className="underline">Política de Privacidade</a>
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

