import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { 
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { 
  Send, 
  Bot, 
  User, 
  Sparkles, 
  Edit, 
  Check, 
  X, 
  RefreshCw,
  FileText,
  MessageSquare,
  Clock,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { apiClient } from '../lib/api.jsx';

export default function ChatInterface({ projectId, questions = [] }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [editingResponse, setEditingResponse] = useState(null);
  const [editedText, setEditedText] = useState('');
  const [generationOptions, setGenerationOptions] = useState({
    tone: 'professional',
    maxWords: null,
    useKnowledgeBase: true
  });
  
  const messagesEndRef = useRef(null);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Mensagem de boas-vindas
    if (messages.length === 0) {
      setMessages([{
        id: 'welcome',
        type: 'system',
        content: 'Olá! Eu sou seu assistente de IA para automação de respostas a RFPs. Selecione uma pergunta para começar a gerar respostas ou digite uma mensagem.',
        timestamp: new Date()
      }]);
    }
  }, []);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Simular resposta do assistente
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: 'Entendi sua mensagem. Para gerar respostas automatizadas, selecione uma pergunta específica da lista ao lado. Posso ajudar você a criar respostas personalizadas, revisar conteúdo existente ou buscar informações na base de conhecimento.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateResponse = async (question) => {
    setIsLoading(true);
    
    const systemMessage = {
      id: Date.now(),
      type: 'system',
      content: `Gerando resposta para: "${question.question_text}"`,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, systemMessage]);

    try {
      const response = await apiClient.generateResponse(question.id, generationOptions);
      
      const responseMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.response_text,
        timestamp: new Date(),
        metadata: {
          questionId: question.id,
          responseId: response.id,
          wordCount: response.word_count,
          confidenceScore: response.confidence_score,
          generatedBy: response.generated_by,
          status: response.status
        }
      };

      setMessages(prev => [...prev, responseMessage]);
      
      // Atualizar pergunta selecionada com nova resposta
      setSelectedQuestion(prev => ({
        ...prev,
        current_response: response
      }));

    } catch (error) {
      console.error('Erro ao gerar resposta:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: `Erro ao gerar resposta: ${error.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditResponse = (message) => {
    setEditingResponse(message.id);
    setEditedText(message.content);
  };

  const handleSaveEdit = async (message) => {
    if (!message.metadata?.responseId) return;

    try {
      setIsLoading(true);
      
      await apiClient.updateResponse(message.metadata.responseId, {
        response_text: editedText,
        status: 'draft'
      });

      setMessages(prev => prev.map(msg => 
        msg.id === message.id 
          ? { ...msg, content: editedText, edited: true }
          : msg
      ));

      setEditingResponse(null);
    } catch (error) {
      console.error('Erro ao salvar edição:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApproveResponse = async (message) => {
    if (!message.metadata?.responseId) return;

    try {
      await apiClient.approveResponse(message.metadata.responseId);
      
      setMessages(prev => prev.map(msg => 
        msg.id === message.id 
          ? { ...msg, metadata: { ...msg.metadata, status: 'approved' } }
          : msg
      ));
    } catch (error) {
      console.error('Erro ao aprovar resposta:', error);
    }
  };

  const getMessageIcon = (type) => {
    switch (type) {
      case 'user': return <User className="h-4 w-4" />;
      case 'assistant': return <Bot className="h-4 w-4" />;
      case 'system': return <Sparkles className="h-4 w-4" />;
      case 'error': return <XCircle className="h-4 w-4" />;
      default: return <MessageSquare className="h-4 w-4" />;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved': return <CheckCircle className="h-3 w-3 text-green-500" />;
      case 'rejected': return <XCircle className="h-3 w-3 text-red-500" />;
      case 'in_review': return <Clock className="h-3 w-3 text-yellow-500" />;
      default: return <Clock className="h-3 w-3 text-gray-500" />;
    }
  };

  return (
    <div className="flex h-full">
      {/* Lista de Perguntas */}
      <div className="w-1/3 border-r bg-muted/30">
        <div className="p-4 border-b">
          <h3 className="font-semibold">Perguntas do RFP</h3>
          <p className="text-sm text-muted-foreground">
            Selecione uma pergunta para gerar resposta
          </p>
        </div>
        
        <ScrollArea className="h-[calc(100vh-200px)]">
          <div className="p-2 space-y-2">
            {questions.map((question) => (
              <Card 
                key={question.id}
                className={`cursor-pointer transition-colors hover:bg-accent ${
                  selectedQuestion?.id === question.id ? 'bg-accent border-primary' : ''
                }`}
                onClick={() => setSelectedQuestion(question)}
              >
                <CardContent className="p-3">
                  <div className="flex items-start justify-between mb-2">
                    <Badge variant="outline" className="text-xs">
                      {question.question_number || `Q${question.id.slice(0, 4)}`}
                    </Badge>
                    {question.required && (
                      <Badge variant="destructive" className="text-xs">
                        Obrigatória
                      </Badge>
                    )}
                  </div>
                  
                  <p className="text-sm font-medium line-clamp-2 mb-2">
                    {question.question_text}
                  </p>
                  
                  {question.section && (
                    <p className="text-xs text-muted-foreground mb-2">
                      Seção: {question.section}
                    </p>
                  )}
                  
                  {question.current_response && (
                    <div className="flex items-center space-x-2 text-xs">
                      {getStatusIcon(question.current_response.status)}
                      <span className="text-muted-foreground">
                        {question.current_response.word_count} palavras
                      </span>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Interface de Chat */}
      <div className="flex-1 flex flex-col">
        {/* Cabeçalho */}
        <div className="p-4 border-b bg-background">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">Chat IA - Geração de Respostas</h2>
              {selectedQuestion && (
                <p className="text-sm text-muted-foreground">
                  Pergunta selecionada: {selectedQuestion.question_number}
                </p>
              )}
            </div>
            
            {selectedQuestion && (
              <div className="flex items-center space-x-2">
                <Dialog>
                  <DialogTrigger asChild>
                    <Button variant="outline" size="sm">
                      <Sparkles className="h-4 w-4 mr-2" />
                      Gerar Resposta
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Opções de Geração</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <label className="text-sm font-medium">Tom da Resposta</label>
                        <Select 
                          value={generationOptions.tone} 
                          onValueChange={(value) => 
                            setGenerationOptions(prev => ({ ...prev, tone: value }))
                          }
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="professional">Profissional</SelectItem>
                            <SelectItem value="formal">Formal</SelectItem>
                            <SelectItem value="friendly">Amigável</SelectItem>
                            <SelectItem value="technical">Técnico</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium">Limite de Palavras</label>
                        <Input
                          type="number"
                          placeholder="Ex: 300"
                          value={generationOptions.maxWords || ''}
                          onChange={(e) => 
                            setGenerationOptions(prev => ({ 
                              ...prev, 
                              maxWords: e.target.value ? parseInt(e.target.value) : null 
                            }))
                          }
                        />
                      </div>
                      
                      <Button 
                        onClick={() => handleGenerateResponse(selectedQuestion)}
                        className="w-full"
                        disabled={isLoading}
                      >
                        {isLoading ? (
                          <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        ) : (
                          <Sparkles className="h-4 w-4 mr-2" />
                        )}
                        Gerar Resposta
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            )}
          </div>
        </div>

        {/* Área de Mensagens */}
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {messages.map((message) => (
              <div key={message.id} className="flex items-start space-x-3">
                <div className={`p-2 rounded-full ${
                  message.type === 'user' ? 'bg-primary text-primary-foreground' :
                  message.type === 'assistant' ? 'bg-blue-500 text-white' :
                  message.type === 'system' ? 'bg-yellow-500 text-white' :
                  'bg-red-500 text-white'
                }`}>
                  {getMessageIcon(message.type)}
                </div>
                
                <div className="flex-1 space-y-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium">
                      {message.type === 'user' ? 'Você' :
                       message.type === 'assistant' ? 'Assistente IA' :
                       message.type === 'system' ? 'Sistema' : 'Erro'}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                    {message.edited && (
                      <Badge variant="secondary" className="text-xs">
                        Editado
                      </Badge>
                    )}
                  </div>
                  
                  <div className="bg-card border rounded-lg p-3">
                    {editingResponse === message.id ? (
                      <div className="space-y-2">
                        <Textarea
                          value={editedText}
                          onChange={(e) => setEditedText(e.target.value)}
                          className="min-h-[100px]"
                        />
                        <div className="flex space-x-2">
                          <Button 
                            size="sm" 
                            onClick={() => handleSaveEdit(message)}
                            disabled={isLoading}
                          >
                            <Check className="h-4 w-4 mr-1" />
                            Salvar
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => setEditingResponse(null)}
                          >
                            <X className="h-4 w-4 mr-1" />
                            Cancelar
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <p className="whitespace-pre-wrap">{message.content}</p>
                        
                        {message.metadata && (
                          <div className="mt-3 pt-3 border-t">
                            <div className="flex items-center justify-between text-xs text-muted-foreground">
                              <div className="flex items-center space-x-4">
                                <span>{message.metadata.wordCount} palavras</span>
                                <span>Confiança: {(message.metadata.confidenceScore * 100).toFixed(0)}%</span>
                                <span>Modelo: {message.metadata.generatedBy}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                {getStatusIcon(message.metadata.status)}
                                <span>{message.metadata.status}</span>
                              </div>
                            </div>
                            
                            <div className="flex space-x-2 mt-2">
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => handleEditResponse(message)}
                              >
                                <Edit className="h-4 w-4 mr-1" />
                                Editar
                              </Button>
                              
                              {message.metadata.status !== 'approved' && (
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  onClick={() => handleApproveResponse(message)}
                                >
                                  <CheckCircle className="h-4 w-4 mr-1" />
                                  Aprovar
                                </Button>
                              )}
                            </div>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-full bg-blue-500 text-white">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="flex-1">
                  <div className="bg-card border rounded-lg p-3">
                    <div className="flex items-center space-x-2">
                      <RefreshCw className="h-4 w-4 animate-spin" />
                      <span>Processando...</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Input de Mensagem */}
        <div className="p-4 border-t">
          <div className="flex space-x-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Digite sua mensagem ou pergunta..."
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              disabled={isLoading}
            />
            <Button 
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

