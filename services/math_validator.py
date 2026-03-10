import re
import sympy as sp
from typing import Tuple, Optional

class MathValidator:
    """
    Mathematical validation layer for verifying calculations
    """
    
    @staticmethod
    def extract_expressions(step: str) -> list:
        """
        Extract mathematical expressions from a step description
        """
        expressions = []
        
        # Split by arrows and look for pure equations
        parts = step.split('→')
        
        for part in parts:
            # Look for equations with = sign in each part
            equation_pattern = r'([^=]+)=([^=]+)'
            matches = re.findall(equation_pattern, part)
            for left, right in matches:
                left_clean = left.strip()
                right_clean = right.strip()
                
                # Only add if both sides look like pure mathematical expressions
                if (MathValidator._is_pure_math_expression(left_clean) and 
                    MathValidator._is_pure_math_expression(right_clean)):
                    expressions.append((left_clean, right_clean))
        
        return expressions
    
    @staticmethod
    def _is_pure_math_expression(expr: str) -> bool:
        """
        Check if a string is a pure mathematical expression (no descriptive words)
        """
        # Remove spaces for checking
        clean_expr = expr.replace(' ', '').strip()
        
        # List of Spanish words that indicate descriptive text
        spanish_words = ['restar', 'dividir', 'simplificar', 'aplicar', 'propiedad', 'manteniendo', 
                        'ambos', 'lados', 'ecuacion', 'variable', 'operacion', 'matematica', 'valida',
                        'correcta', 'precisa', 'resultado', 'orden', 'despeja', 'sigue']
        
        # Check if it contains Spanish descriptive words
        if any(word in expr.lower() for word in spanish_words):
            return False
        
        # Check if it has mathematical content
        math_indicators = ['+', '-', '*', '/', 'x', 'y', 'z', '^', '√', '²', '³', '(', ')', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        
        return any(indicator in clean_expr for indicator in math_indicators) and len(clean_expr) > 0
    
    @staticmethod
    def evaluate_expression(expr: str) -> Optional[float]:
        """
        Safely evaluate a mathematical expression
        """
        try:
            # Replace common mathematical symbols
            expr = expr.replace('×', '*').replace('÷', '/').replace('²', '**2').replace('³', '**3')
            
            # Use sympy for safe evaluation
            result = sp.sympify(expr)
            if result.is_number:
                return float(result.evalf())
            return None
        except:
            return None
    
    @staticmethod
    def verify_equation(left: str, right: str) -> Tuple[bool, str]:
        """
        Verify if left side equals right side
        """
        try:
            # Replace common mathematical symbols
            left_clean = left.replace('×', '*').replace('÷', '/').replace('²', '**2').replace('³', '**3')
            right_clean = right.replace('×', '*').replace('÷', '/').replace('²', '**2').replace('³', '**3')
            
            # Add multiplication symbols between variables and numbers (e.g., "2x" -> "2*x")
            left_clean = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', left_clean)
            right_clean = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', right_clean)
            
            # Parse expressions with sympy
            left_expr = sp.sympify(left_clean)
            right_expr = sp.sympify(right_clean)
            
            # Check if they are equivalent
            difference = sp.simplify(left_expr - right_expr)
            
            if difference == 0:
                return True, f"Verification passed: {left} = {right}"
            else:
                return False, f"Verification failed: {left} ≠ {right} (difference: {difference})"
                
        except Exception as e:
            # If we can't evaluate algebraically, try numeric evaluation for pure numbers
            try:
                left_val = MathValidator.evaluate_expression(left)
                right_val = MathValidator.evaluate_expression(right)
                
                if left_val is not None and right_val is not None:
                    if abs(left_val - right_val) < 1e-10:
                        return True, f"Numeric verification passed: {left_val} = {right_val}"
                    else:
                        return False, f"Numeric verification failed: {left_val} ≠ {right_val}"
                else:
                    return False, f"Cannot evaluate expressions: {str(e)}"
            except:
                return False, f"Cannot verify equation: {str(e)}"
    
    @staticmethod
    def validate_step(step: str) -> Tuple[bool, str]:
        """
        Validate a mathematical step with simplified logic
        """
        expressions = MathValidator.extract_expressions(step)
        
        if not expressions:
            return True, "No verifiable expressions found"
        
        all_valid = True
        messages = []
        
        for left, right in expressions:
            # For numeric expressions, verify equality
            if MathValidator._is_numeric_expression(left) and MathValidator._is_numeric_expression(right):
                is_valid, message = MathValidator._verify_numeric_equality(left, right)
                all_valid = all_valid and is_valid
                messages.append(message)
            # For algebraic expressions, just check syntax
            elif MathValidator._is_algebraic_expression(left) and MathValidator._is_algebraic_expression(right):
                is_valid, message = MathValidator._verify_algebraic_syntax(left, right)
                all_valid = all_valid and is_valid
                messages.append(message)
            else:
                messages.append(f"Mixed expression types: {left} = {right}")
        
        return all_valid, "; ".join(messages)
    
    @staticmethod
    def _is_numeric_expression(expr: str) -> bool:
        """Check if expression contains only numbers and operators"""
        clean_expr = expr.replace(' ', '').replace('*', '').replace('/', '').replace('+', '').replace('-', '').replace('(', '').replace(')', '')
        return clean_expr.isdigit() or clean_expr.replace('.', '').isdigit()
    
    @staticmethod
    def _is_algebraic_expression(expr: str) -> bool:
        """Check if expression contains variables"""
        return any(char in expr for char in 'xyz')
    
    @staticmethod
    def _verify_numeric_equality(left: str, right: str) -> Tuple[bool, str]:
        """Verify if two numeric expressions are equal"""
        try:
            left_val = MathValidator.evaluate_expression(left)
            right_val = MathValidator.evaluate_expression(right)
            
            if left_val is not None and right_val is not None:
                if abs(left_val - right_val) < 1e-10:
                    return True, f"Numeric verification passed: {left_val} = {right_val}"
                else:
                    return False, f"Numeric verification failed: {left_val} ≠ {right_val}"
            else:
                return False, f"Cannot evaluate numeric expressions"
        except:
            return False, f"Error in numeric evaluation"
    
    @staticmethod
    def _verify_algebraic_syntax(left: str, right: str) -> Tuple[bool, str]:
        """Just verify algebraic expressions have valid syntax"""
        try:
            # Clean expressions
            left_clean = left.replace('×', '*').replace('÷', '/')
            right_clean = right.replace('×', '*').replace('÷', '/')
            
            # Add multiplication symbols
            left_clean = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', left_clean)
            right_clean = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', right_clean)
            
            # Try to parse (syntax check)
            sp.sympify(left_clean)
            sp.sympify(right_clean)
            
            return True, f"Algebraic syntax valid: {left} = {right}"
        except:
            return False, f"Invalid algebraic syntax: {left} = {right}"
    
    @staticmethod
    def check_algebraic_manipulation(original: str, transformed: str) -> Tuple[bool, str]:
        """
        Check if algebraic manipulation is mathematically valid
        """
        try:
            # Parse both expressions
            orig_expr = sp.sympify(original.replace('×', '*').replace('÷', '/'))
            trans_expr = sp.sympify(transformed.replace('×', '*').replace('÷', '/'))
            
            # Check if they are equivalent
            if sp.simplify(orig_expr - trans_expr) == 0:
                return True, "Algebraic manipulation is correct"
            else:
                return False, f"Expressions are not equivalent: {original} ≠ {transformed}"
                
        except Exception as e:
            return False, f"Cannot verify algebraic manipulation: {str(e)}"
