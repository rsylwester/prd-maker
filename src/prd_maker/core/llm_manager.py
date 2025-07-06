"""LLM management and integration with LangChain."""

from typing import Optional, Dict, List
from langchain.llms.base import LLM
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

load_dotenv()


class LLMManager:
    """Manages different LLM providers and models."""
    
    def __init__(self):
        self._models: Dict[str, LLM] = {}
        self._current_model: Optional[str] = None
        self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Initialize models with available API keys."""
        # OpenAI models
        if os.getenv("OPENAI_API_KEY"):
            try:
                self.add_openai_model("gpt-4", os.getenv("OPENAI_API_KEY"))
                self.add_openai_model("gpt-3.5-turbo", os.getenv("OPENAI_API_KEY"))
            except Exception:
                pass
        
        # Anthropic models
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                self.add_anthropic_model("claude-3-sonnet-20240229", os.getenv("ANTHROPIC_API_KEY"))
                self.add_anthropic_model("claude-3-haiku-20240307", os.getenv("ANTHROPIC_API_KEY"))
            except Exception:
                pass
        
        # Ollama models (local)
        try:
            self.add_ollama_model("llama2")
            self.add_ollama_model("mistral")
        except Exception:
            pass
    
    def add_openai_model(self, model_name: str = "gpt-4", api_key: str = None) -> None:
        """Add OpenAI model to available models."""
        self._models[f"openai_{model_name}"] = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            temperature=0.7
        )
    
    def add_anthropic_model(self, model_name: str = "claude-3-sonnet-20240229", api_key: str = None) -> None:
        """Add Anthropic model to available models."""
        self._models[f"anthropic_{model_name}"] = ChatAnthropic(
            model=model_name,
            api_key=api_key,
            temperature=0.7
        )
    
    def add_ollama_model(self, model_name: str = "llama2", base_url: str = "http://localhost:11434") -> None:
        """Add Ollama model to available models."""
        self._models[f"ollama_{model_name}"] = ChatOllama(
            model=model_name,
            base_url=base_url,
            temperature=0.7
        )
    
    def set_current_model(self, model_key: str) -> None:
        """Set the current active model."""
        if model_key not in self._models:
            raise ValueError(f"Model {model_key} not found")
        self._current_model = model_key
    
    def get_current_model(self) -> Optional[LLM]:
        """Get the current active model."""
        if self._current_model is None:
            return None
        return self._models[self._current_model]
    
    def list_models(self) -> List[str]:
        """List all available models."""
        return list(self._models.keys())
    
    def generate_text(self, prompt: str, system_message: str = None, **kwargs) -> str:
        """Generate text using the current model."""
        model = self.get_current_model()
        if model is None:
            raise ValueError("No model selected")
        
        messages = []
        if system_message:
            messages.append(SystemMessage(content=system_message))
        messages.append(HumanMessage(content=prompt))
        
        response = model.invoke(messages, **kwargs)
        return response.content if hasattr(response, 'content') else str(response)
    
    def generate_questions(self, project_description: str) -> List[str]:
        """Generate planning questions based on project description."""
        system_message = """Jesteś doświadczonym menedżerem produktu, którego zadaniem jest pomoc w stworzeniu kompleksowego dokumentu wymagań projektowych (PRD) na podstawie dostarczonych informacji. Twoim celem jest wygenerowanie listy pytań i zaleceń, które zostaną wykorzystane w kolejnym promptowaniu do utworzenia pełnego PRD.

Przeanalizuj dostarczone informacje, koncentrując się na aspektach istotnych dla tworzenia PRD. Rozważ następujące kwestie:
1. Zidentyfikuj główny problem, który produkt ma rozwiązać.
2. Określ kluczowe funkcjonalności MVP.
3. Rozważ potencjalne historie użytkownika i ścieżki korzystania z produktu.
4. Pomyśl o kryteriach sukcesu i sposobach ich mierzenia.
5. Oceń ograniczenia projektowe i ich wpływ na rozwój produktu.

Na podstawie analizy wygeneruj listę pytań. Powinny one dotyczyć wszelkich niejasności, potencjalnych problemów lub obszarów, w których potrzeba więcej informacji, aby stworzyć skuteczny PRD. Rozważ pytania dotyczące:
1. Szczegółów problemu użytkownika
2. Priorytetyzacji funkcjonalności
3. Oczekiwanego doświadczenia użytkownika
4. Mierzalnych wskaźników sukcesu
5. Potencjalnych ryzyk i wyzwań
6. Harmonogramu i zasobów

Zwróć wyłącznie pytania w języku polskim, ponumerowane dla jasności. Każde pytanie w osobnej linii."""
        
        prompt = f"""Na podstawie poniższego opisu projektu:

{project_description}

Wygeneruj listę 8-12 szczegółowych pytań, które pomogą doprecyzować wymagania do stworzenia kompleksowego PRD."""
        
        response = self.generate_text(prompt, system_message)
        questions = [q.strip() for q in response.split('\n') if q.strip() and not q.strip().startswith('#') and q.strip()]
        return questions[:12]  # Limit to 12 questions
    
    def generate_project_description(self, project_idea: str) -> str:
        """Generate detailed project description from basic idea."""
        system_message = """You are a product management expert. Transform basic project ideas into structured, comprehensive project descriptions. Include:
        - Clear problem statement
        - Target audience
        - Core value proposition
        - Key features overview
        - Business goals
        
        Write in Polish and be specific and actionable."""
        
        prompt = f"""Transform this project idea into a comprehensive project description:

        {project_idea}
        
        Create a detailed description that covers the problem, solution, target users, and key features."""
        
        return self.generate_text(prompt, system_message)
    
    def generate_planning_summary(self, project_description: str, qa_history: List[Dict[str, str]]) -> str:
        """Generate planning summary from Q&A session."""
        system_message = """Jesteś asystentem AI, którego zadaniem jest podsumowanie rozmowy na temat planowania PRD (Product Requirements Document) dla MVP i przygotowanie zwięzłego podsumowania dla następnego etapu rozwoju.

Twoim zadaniem jest:
1. Podsumować historię konwersacji, koncentrując się na wszystkich decyzjach związanych z planowaniem PRD.
2. Przygotować szczegółowe podsumowanie rozmowy, które obejmuje:
   a. Główne wymagania funkcjonalne produktu
   b. Kluczowe historie użytkownika i ścieżki korzystania
   c. Ważne kryteria sukcesu i sposoby ich mierzenia
   d. Wszelkie nierozwiązane kwestie lub obszary wymagające dalszego wyjaśnienia

Sformatuj wyniki w następujący sposób (używaj formatu markdown):

## Decyzje podjęte podczas sesji
[Wymień decyzje podjęte przez użytkownika, ponumerowane]

## Główne wymagania funkcjonalne
[Lista kluczowych funkcjonalności produktu]

## Kluczowe historie użytkownika
[Zidentyfikowane user stories i ścieżki użytkownika]

## Kryteria sukcesu i metryki
[Sposoby mierzenia sukcesu produktu]

## Uwagi techniczne i ograniczenia
[Kwestie techniczne, ograniczenia, ryzyka]

## Nierozwiązane kwestie
[Obszary wymagające dalszych wyjaśnień, jeśli takie istnieją]

Końcowy wynik powinien być jasny, zwięzły i zawierać cenne informacje dla następnego etapu tworzenia PRD."""
        
        qa_text = "\n".join([f"Pytanie: {qa['question']}\nOdpowiedź: {qa['answer']}" for qa in qa_history if qa.get('answer', '').strip()])
        
        prompt = f"""Na podstawie poniższych informacji z sesji planistycznej stwórz strukturalne podsumowanie:

## OPIS PROJEKTU:
{project_description}

## HISTORIA ROZMOWY (PYTANIA I ODPOWIEDZI):
{qa_text}

Przeanalizuj wszystkie informacje i stwórz kompleksowe podsumowanie zgodnie z podanym formatem."""
        
        return self.generate_text(prompt, system_message)
    
    def generate_prd_document(self, planning_summary: str) -> str:
        """Generate final PRD document from planning summary."""
        system_message = """Jesteś doświadczonym menedżerem produktu, którego zadaniem jest stworzenie kompleksowego dokumentu wymagań produktu (PRD) w oparciu o poniższe opisy.

Wykonaj następujące kroki, aby stworzyć kompleksowy i dobrze zorganizowany dokument:

1. Podziel PRD na następujące sekcje:
   a. Przegląd produktu
   b. Problem użytkownika
   c. Wymagania funkcjonalne
   d. Granice produktu
   e. Historyjki użytkowników
   f. Metryki sukcesu

2. W każdej sekcji należy podać szczegółowe i istotne informacje w oparciu o podsumowanie sesji planistycznej. Upewnij się, że:
   - Używasz jasnego i zwięzłego języka
   - W razie potrzeby podajesz konkretne szczegóły i dane
   - Zachowujesz spójność w całym dokumencie
   - Odnosisz się do wszystkich punktów wymienionych w każdej sekcji

3. Podczas tworzenia historyjek użytkownika i kryteriów akceptacji:
   - Wymień WSZYSTKIE niezbędne historyjki użytkownika, w tym scenariusze podstawowe, alternatywne i skrajne
   - Przypisz unikalny identyfikator wymagań (np. US-001) do każdej historyjki użytkownika
   - Uwzględnij co najmniej jedną historię użytkownika specjalnie dla bezpiecznego dostępu lub uwierzytelniania, jeśli aplikacja wymaga identyfikacji użytkownika
   - Upewnij się, że żadna potencjalna interakcja użytkownika nie została pominięta
   - Upewnij się, że każda historia użytkownika jest testowalna

Użyj następującej struktury dla każdej historii użytkownika:
- ID (US-001, US-002, etc.)
- Tytuł
- Opis (w formacie "Jako [użytkownik] chcę [akcja] aby [cel]")
- Kryteria akceptacji (lista punktów)

4. Formatowanie PRD:
   - Zachowaj spójne formatowanie i numerację
   - Nie używaj pogrubionego formatowania w markdown (**)
   - Wymień WSZYSTKIE historyjki użytkownika
   - Sformatuj PRD w poprawnym markdown

Przygotuj PRD z następującą strukturą:

# Dokument wymagań produktu (PRD) - [Nazwa produktu]
## 1. Przegląd produktu
## 2. Problem użytkownika
## 3. Wymagania funkcjonalne
## 4. Granice produktu
## 5. Historyjki użytkowników
## 6. Metryki sukcesu

Pamiętaj, aby wypełnić każdą sekcję szczegółowymi, istotnymi informacjami. Upewnij się, że PRD jest wyczerpujący, jasny i zawiera wszystkie istotne informacje potrzebne do dalszej pracy nad produktem.

Ostateczny wynik powinien składać się wyłącznie z PRD zgodnego ze wskazanym formatem w markdown."""
        
        prompt = f"""Na podstawie poniższego podsumowania sesji planistycznej stwórz kompletny dokument PRD:

{planning_summary}

Stwórz kompleksowy PRD ze wszystkimi wymaganymi sekcjami, sformatowany w Markdown zgodnie z podaną strukturą."""
        
        return self.generate_text(prompt, system_message)