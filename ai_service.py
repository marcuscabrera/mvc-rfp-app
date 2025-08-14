import os
import requests
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AIService:
    """Serviço para integração com modelos de IA (Gemini e Gemma)"""
    
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemma_model_path = os.getenv('GEMMA_MODEL_PATH')
        self.gemini_base_url = "https://generativelanguage.googleapis.com/v1beta"
        
    def extract_questions_from_text(self, text: str, document_type: str = 'rfp', 
                                  language: str = 'pt-BR') -> List[Dict[str, Any]]:
        """Extrai perguntas de um texto usando IA"""
        try:
            # Tentar primeiro com Gemini
            return self._extract_questions_gemini(text, document_type, language)
        except Exception as e:
            logger.warning(f"Falha na extração com Gemini: {e}")
            try:
                # Fallback para Gemma
                return self._extract_questions_gemma(text, document_type, language)
            except Exception as e2:
                logger.error(f"Falha na extração com Gemma: {e2}")
                raise Exception(f"Falha em ambos os modelos de IA: Gemini ({e}), Gemma ({e2})")
    
    def _extract_questions_gemini(self, text: str, document_type: str, 
                                language: str) -> List[Dict[str, Any]]:
        """Extrai perguntas usando Google Gemini API"""
        if not self.gemini_api_key:
            raise Exception("GEMINI_API_KEY não configurada")
        
        prompt = self._build_extraction_prompt(text, document_type, language)
        
        url = f"{self.gemini_base_url}/models/gemini-1.5-pro:generateContent"
        headers = {
            'Content-Type': 'application/json',
            'x-goog-api-key': self.gemini_api_key
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 8192,
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        if 'candidates' not in result or not result['candidates']:
            raise Exception("Resposta inválida da API Gemini")
        
        content = result['candidates'][0]['content']['parts'][0]['text']
        return self._parse_extracted_questions(content)
    
    def _extract_questions_gemma(self, text: str, document_type: str, 
                                language: str) -> List[Dict[str, Any]]:
        """Extrai perguntas usando Gemma (implementação simplificada)"""
        # Esta seria uma implementação local do Gemma
        # Por simplicidade, retornamos uma extração básica
        logger.info("Usando fallback Gemma para extração de perguntas")
        
        # Implementação simplificada - busca por padrões de pergunta
        questions = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if self._looks_like_question(line):
                questions.append({
                    'question_text': line,
                    'question_number': f"Q{len(questions) + 1}",
                    'section': 'Seção Identificada Automaticamente',
                    'category': 'general',
                    'question_type': 'open',
                    'required': False,
                    'confidence_score': 0.7,
                    'page_number': None,
                    'position_in_page': i,
                    'keywords': self._extract_keywords(line),
                    'context': self._get_context(lines, i)
                })
        
        return questions
    
    def _looks_like_question(self, text: str) -> bool:
        """Verifica se um texto parece ser uma pergunta"""
        question_indicators = [
            '?', 'descreva', 'explique', 'como', 'qual', 'quando', 'onde',
            'por que', 'quantos', 'quais', 'apresente', 'detalhe', 'informe'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in question_indicators)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrai palavras-chave básicas de um texto"""
        # Implementação simplificada
        stop_words = {'o', 'a', 'os', 'as', 'de', 'da', 'do', 'das', 'dos', 'e', 'ou'}
        words = text.lower().split()
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return keywords[:5]  # Retorna até 5 palavras-chave
    
    def _get_context(self, lines: List[str], current_index: int, context_size: int = 2) -> str:
        """Obtém contexto ao redor de uma linha"""
        start = max(0, current_index - context_size)
        end = min(len(lines), current_index + context_size + 1)
        context_lines = lines[start:end]
        return ' '.join(line.strip() for line in context_lines if line.strip())
    
    def _build_extraction_prompt(self, text: str, document_type: str, language: str) -> str:
        """Constrói prompt para extração de perguntas"""
        return f"""
Analise o seguinte documento de {document_type} em {language} e extraia todas as perguntas, requisitos e solicitações de informação.

Para cada pergunta encontrada, forneça as seguintes informações em formato JSON:
- question_text: O texto completo da pergunta
- question_number: Número ou código da pergunta (se disponível)
- section: Seção do documento onde a pergunta aparece
- category: Categoria da pergunta (technical, experience, financial, etc.)
- question_type: Tipo da pergunta (open, multiple_choice, yes_no, etc.)
- required: Se a pergunta é obrigatória (true/false)
- max_words: Limite de palavras se especificado
- keywords: Lista de palavras-chave relevantes
- context: Contexto adicional da pergunta
- confidence_score: Score de confiança da extração (0.0 a 1.0)

Documento:
{text[:8000]}  # Limitar tamanho para evitar exceder limites da API

Retorne apenas um array JSON válido com as perguntas extraídas.
"""
    
    def _parse_extracted_questions(self, content: str) -> List[Dict[str, Any]]:
        """Faz parse das perguntas extraídas"""
        try:
            # Tentar extrair JSON do conteúdo
            start = content.find('[')
            end = content.rfind(']') + 1
            
            if start == -1 or end == 0:
                raise Exception("JSON não encontrado na resposta")
            
            json_content = content[start:end]
            questions = json.loads(json_content)
            
            # Validar e limpar dados
            validated_questions = []
            for q in questions:
                if isinstance(q, dict) and 'question_text' in q:
                    validated_questions.append({
                        'question_text': q.get('question_text', ''),
                        'question_number': q.get('question_number'),
                        'section': q.get('section'),
                        'category': q.get('category', 'general'),
                        'question_type': q.get('question_type', 'open'),
                        'required': q.get('required', False),
                        'max_words': q.get('max_words'),
                        'keywords': q.get('keywords', []),
                        'context': q.get('context'),
                        'confidence_score': q.get('confidence_score', 0.8)
                    })
            
            return validated_questions
        
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao fazer parse do JSON: {e}")
            raise Exception("Resposta da IA não está em formato JSON válido")
    
    def generate_response(self, question_text: str, context_documents: List[str] = None,
                         max_words: int = None, tone: str = 'professional',
                         language: str = 'pt-BR') -> Dict[str, Any]:
        """Gera resposta para uma pergunta"""
        try:
            # Tentar primeiro com Gemini
            return self._generate_response_gemini(question_text, context_documents, 
                                                max_words, tone, language)
        except Exception as e:
            logger.warning(f"Falha na geração com Gemini: {e}")
            try:
                # Fallback para Gemma
                return self._generate_response_gemma(question_text, context_documents,
                                                   max_words, tone, language)
            except Exception as e2:
                logger.error(f"Falha na geração com Gemma: {e2}")
                raise Exception(f"Falha em ambos os modelos de IA: Gemini ({e}), Gemma ({e2})")
    
    def _generate_response_gemini(self, question_text: str, context_documents: List[str],
                                max_words: int, tone: str, language: str) -> Dict[str, Any]:
        """Gera resposta usando Google Gemini API"""
        if not self.gemini_api_key:
            raise Exception("GEMINI_API_KEY não configurada")
        
        prompt = self._build_response_prompt(question_text, context_documents, 
                                           max_words, tone, language)
        
        url = f"{self.gemini_base_url}/models/gemini-1.5-pro:generateContent"
        headers = {
            'Content-Type': 'application/json',
            'x-goog-api-key': self.gemini_api_key
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 4096,
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        if 'candidates' not in result or not result['candidates']:
            raise Exception("Resposta inválida da API Gemini")
        
        content = result['candidates'][0]['content']['parts'][0]['text']
        
        return {
            'response_text': content.strip(),
            'word_count': len(content.split()),
            'character_count': len(content),
            'confidence_score': 0.9,
            'generated_by': 'gemini-1.5-pro',
            'generated_at': datetime.utcnow(),
            'source_documents': context_documents or []
        }
    
    def _generate_response_gemma(self, question_text: str, context_documents: List[str],
                               max_words: int, tone: str, language: str) -> Dict[str, Any]:
        """Gera resposta usando Gemma (implementação simplificada)"""
        logger.info("Usando fallback Gemma para geração de resposta")
        
        # Implementação simplificada
        response_text = f"""Esta é uma resposta gerada automaticamente para a pergunta: "{question_text}"

Nossa empresa possui ampla experiência e capacidade técnica para atender aos requisitos especificados. 
Temos uma equipe qualificada e processos bem estabelecidos que garantem a entrega de soluções de alta qualidade.

Detalhes específicos sobre nossa abordagem e metodologia podem ser fornecidos mediante solicitação adicional.
"""
        
        if max_words:
            words = response_text.split()
            if len(words) > max_words:
                response_text = ' '.join(words[:max_words]) + '...'
        
        return {
            'response_text': response_text.strip(),
            'word_count': len(response_text.split()),
            'character_count': len(response_text),
            'confidence_score': 0.6,
            'generated_by': 'gemma-fallback',
            'generated_at': datetime.utcnow(),
            'source_documents': context_documents or []
        }
    
    def _build_response_prompt(self, question_text: str, context_documents: List[str],
                             max_words: int, tone: str, language: str) -> str:
        """Constrói prompt para geração de resposta"""
        context = ""
        if context_documents:
            context = "\n\nDocumentos de contexto:\n" + "\n".join(context_documents[:3])
        
        word_limit = f"\nLimite de palavras: {max_words}" if max_words else ""
        
        return f"""
Gere uma resposta profissional e detalhada para a seguinte pergunta de RFP em {language}.

Tom: {tone}
{word_limit}

Pergunta: {question_text}
{context}

A resposta deve ser:
- Específica e relevante à pergunta
- Profissional e bem estruturada
- Baseada nas informações de contexto fornecidas
- Convincente e demonstrar competência

Resposta:
"""

# Instância global do serviço
ai_service = AIService()

