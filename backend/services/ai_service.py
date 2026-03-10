import json
from typing import List, Dict, Any
from openai import OpenAI
from config.settings import settings
from models.request_models import StepAnalysis, SolveResponse
from services.math_validator import MathValidator


class AIService:
    def __init__(self):
        # Clean environment variables that might cause issues
        import os
        env_vars_to_remove = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'proxies']
        for var in env_vars_to_remove:
            if var in os.environ:
                del os.environ[var]
        
        self.client = OpenAI(
            api_key=settings.ai_api_key,
            base_url=settings.ai_base_url
        )
    
    async def analyze_solution(self, problem: str, student_solution: str) -> SolveResponse:
        """
        Analyze student's math solution using AI with enhanced precision
        """
        prompt = self._build_prompt(problem, student_solution)
        
        try:
            response = self.client.chat.completions.create(
                model=settings.ai_model,
                messages=[
                    {"role": "system", "content": "Eres un experto matemático con rigor absoluto. Evalúa soluciones matemáticas con precisión matemática perfecta. Detecta cualquier error por mínimo que sea. No aceptes aproximaciones ni pasos 'casi correctos'. Cada operación debe ser matemáticamente exacta."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Enhanced error handling for empty or invalid responses
            if not content or content.strip() == "":
                raise ValueError("Empty response from AI")
            
            return self._parse_response(content)
            
        except Exception as e:
            # Enhanced error handling with specific error types
            error_msg = f"AI service error: {str(e)}"
            
            if "openai" in str(e).lower() or "api" in str(e).lower():
                error_msg = "AI API connection error. Please check your API configuration."
            elif "timeout" in str(e).lower():
                error_msg = "AI service timeout. Please try again."
            elif "rate" in str(e).lower():
                error_msg = "AI rate limit exceeded. Please try again later."
            
            raise Exception(error_msg)
    
    def _build_prompt(self, problem: str, student_solution: str) -> str:
        """
        Build prompt for AI analysis
        """
        # Split student solution into numbered lines for clarity
        lines = student_solution.split('\n')
        numbered_solution = ""
        for i, line in enumerate(lines, 1):
            numbered_solution += f"LÍNEA {i}: {line}\n"
        
        return f"""
Eres un evaluador matemático preciso. Analiza las LÍNEAS de la solución del estudiante que están numeradas.

PROBLEMA MATEMÁTICO:
{problem}

SOLUCIÓN DEL ESTUDIANTE (analiza ÚNICAMENTE las líneas numeradas abajo):
{numbered_solution}

INSTRUCCIONES CRÍTICAS:
1. Responde ÚNICAMENTE con JSON válido. Sin texto adicional.
2. Analiza SOLAMENTE las líneas que dicen "LÍNEA 1:", "LÍNEA 2:", etc.
3. NO incluyas el problema en tu análisis.
4. Cada "LÍNEA X:" es un paso separado en tu análisis.
5. Si hay 2 líneas numeradas, tu análisis debe tener exactamente 2 pasos.
6. Usa el texto exacto de cada línea numerada en el campo "step".

EJEMPLO:
Si ves:
LÍNEA 1: 2x = 15 - 5
LÍNEA 2: 2x = 10

Tu JSON debe tener:
{{
    "analysis": [
        {{
            "step": "2x = 15 - 5",
            "status": "correcto",
            "explanation": "..."
        }},
        {{
            "step": "2x = 10", 
            "status": "correcto",
            "explanation": "..."
        }}
    ]
}}

CRITERIOS DE EVALUACIÓN:

PASO CORRECTO si:
- La operación matemática es correcta
- Sigue las reglas y propiedades matemáticas aplicables
- El resultado es preciso
- La notación matemática es estándar
- El razonamiento lógico es matemáticamente válido

PASO INCORRECTO si:
- Hay un error matemático real
- Operación mal ejecutada (errores de signo, cálculo, orden)
- Aplicación incorrecta de propiedades o fórmulas
- Resultado numérico incorrecto
- Razonamiento lógico matemáticamente inválido

FORMATO JSON EXIGIDO:
{{
    "analysis": [
        {{
            "step": "texto exacto de la línea numerada sin 'LÍNEA X:'",
            "status": "correcto" o "incorrecto",
            "explanation": "explicación matemática clara. Si es correcto: justificación matemática. Si es incorrecto: identificación del error y corrección."
        }}
    ],
    "correct_solution": "solución matemáticamente correcta paso a paso. Cada operación: operación = resultado. Usa notación estándar."

REQUISITOS IMPORTANTES:
- Usa el texto EXACTO de cada línea numerada (sin el prefijo "LÍNEA X:")
- NO incluyas el problema
- Cada línea numerada = un paso en el análisis
- Todas las respuestas en español
- Sé preciso pero justo en evaluación
"""
    
    def _parse_response(self, content: str) -> SolveResponse:
        """
        Parse AI response into SolveResponse format with mathematical validation
        """
        try:
            # Try to extract JSON from the response
            # Look for JSON between ```json and ``` markers first
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                if end != -1:
                    json_str = content[start:end].strip()
                else:
                    # If no closing ```, take everything after ```json
                    json_str = content[start:].strip()
            else:
                # Fallback: look for first { and last }
                start = content.find('{')
                end = content.rfind('}') + 1
                
                if start == -1 or end == 0:
                    raise ValueError("No JSON found in response")
                
                json_str = content[start:end]
            
            # Clean up the JSON string
            json_str = json_str.replace('\n', ' ').replace('\r', '')
            
            data = json.loads(json_str)
            
            # Convert to StepAnalysis objects with validation
            analysis = []
            for step_data in data.get('analysis', []):
                step_text = step_data['step']
                ai_status = step_data['status']
                ai_explanation = step_data['explanation']
                
                # Perform mathematical validation only if enabled
                is_valid = True
                validation_result = "Validation disabled"
                validation_failed = False
                
                if settings.math_validation_enabled:
                    is_valid, validation_result = MathValidator.validate_step(step_text)
                    # Only consider it a failure if validation explicitly says false (not just "cannot evaluate")
                    validation_failed = (not is_valid and "Cannot evaluate" not in validation_result and "Cannot verify" not in validation_result)
                
                # Override AI status if mathematical validation explicitly fails
                final_status = ai_status
                final_explanation = ai_explanation
                
                if ai_status == 'correcto' and validation_failed:
                    final_status = 'incorrecto'
                    final_explanation = f"{ai_explanation} [VALIDACIÓN MATEMÁTICA: {validation_result}]"
                elif ai_status == 'correcto':
                    if settings.math_validation_enabled:
                        final_explanation = f"{ai_explanation} [VALIDACIÓN MATEMÁTICA: {validation_result}]"
                elif ai_status == 'incorrecto':
                    if settings.math_validation_enabled:
                        final_explanation = f"{ai_explanation} [VALIDACIÓN MATEMÁTICA: {validation_result}]"
                
                analysis.append(StepAnalysis(
                    step=step_text,
                    status=final_status,
                    explanation=final_explanation
                ))
            
            # Ensure correct_solution is a string
            correct_solution = data.get('correct_solution', 'No correct solution provided.')
            if isinstance(correct_solution, list):
                # If it's a list, join it into a string
                correct_solution = '\n'.join(str(item) for item in correct_solution)
            elif not isinstance(correct_solution, str):
                # Convert any other type to string
                correct_solution = str(correct_solution)
            
            return SolveResponse(
                analysis=analysis,
                correct_solution=correct_solution
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback response if parsing fails
            return SolveResponse(
                analysis=[
                    StepAnalysis(
                        step="Unable to parse AI response",
                        status="incorrecto",
                        explanation=f"There was an error processing the AI response: {str(e)}. Raw response: {content[:300]}..."
                    )
                ],
                correct_solution="Please try again or contact support."
            )


# Create a singleton instance
ai_service = AIService()
