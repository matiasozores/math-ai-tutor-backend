#!/usr/bin/env python3
"""
Test script for AI Math Tutor API
"""

import requests
import json

def test_api():
    """Test the solve endpoint with a sample math problem"""
    
    # Test case 1: Simple linear equation
    test_case_1 = {
        "problem": "Resuelve para x: 2x + 5 = 15",
        "student_solution": """2x + 5 = 15
2x = 15 - 5
2x = 10
x = 10 / 2
x = 5"""
    }
    
    # Test case 2: Quadratic equation (with mistake)
    test_case_2 = {
        "problem": "Resuelve: x² - 5x + 6 = 0",
        "student_solution": """x² - 5x + 6 = 0
(x - 2)(x - 3) = 0
x - 2 = 0, x - 3 = 0
x = 2, x = 3
Verificación: (2)² - 5(2) + 6 = 4 - 10 + 6 = 0 ✓"""
    }
    
    # Test case 3: Arithmetic with error
    test_case_3 = {
        "problem": "Calcula: (15 + 8) × 3 - 12 ÷ 4",
        "student_solution": """(15 + 8) × 3 - 12 ÷ 4
23 × 3 - 12 ÷ 4
69 - 3
66"""
    }
    
    base_url = "http://localhost:8000"
    
    print("🧮 Probando API de AI Math Tutor")
    print("=" * 50)
    
    for i, test_case in enumerate([test_case_1, test_case_2, test_case_3], 1):
        print(f"\n📝 Test Case {i}:")
        print(f"Problema: {test_case['problem']}")
        print(f"Solución del estudiante:\n{test_case['student_solution']}")
        print("\n⏳ Enviando a la API...")
        
        try:
            response = requests.post(
                f"{base_url}/api/solve",
                json=test_case,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Respuesta exitosa!")
                print("\n📊 Análisis de pasos:")
                
                for j, step in enumerate(result['analysis'], 1):
                    status_icon = "✅" if step['status'] == 'correct' else "❌"
                    print(f"  {j}. {status_icon} {step['step']}")
                    if step['explanation']:
                        print(f"     💡 {step['explanation']}")
                
                print(f"\n🎯 Solución correcta:")
                print(result['correct_solution'])
                
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ No se puede conectar al servidor. Asegúrate de que el backend esté corriendo en http://localhost:8000")
        except requests.exceptions.Timeout:
            print("❌ Timeout. La API está tardando demasiado en responder.")
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
        
        print("\n" + "-" * 50)
    
    print("\n🎉 Pruebas completadas!")
    print("\n💡 Para probar la interfaz web:")
    print("1. Asegúrate que el backend esté corriendo: uvicorn main:app --reload")
    print("2. Inicia el frontend: cd ../frontend && npm run dev")
    print("3. Abre http://localhost:3000 en tu navegador")

if __name__ == "__main__":
    test_api()
