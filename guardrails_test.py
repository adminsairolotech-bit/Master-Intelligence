#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Guardrails - Rules Enforcer for LLMs
Validates, filters, and shapes LLM outputs
"""

from guardrails import Guard, Validator, register_validator

@register_validator(name="contains-technical-term", data_type="string")
class ContainsTechnicalTerm(Validator):
    def __init__(self, on_fail=None, **kwargs):
        super().__init__(on_fail=on_fail, **kwargs)
        self.tech_terms = ['python', 'api', 'function', 'code', 'javascript', 'data']

    def validate(self, value, schema=None):
        text_lower = value.lower() if isinstance(value, str) else str(value)
        for term in self.tech_terms:
            if term in text_lower:
                return value
        raise Exception("Must contain technical term")

@register_validator(name="min-length-custom", data_type="string")
class MinLength(Validator):
    def __init__(self, min_length=10, on_fail=None, **kwargs):
        super().__init__(on_fail=on_fail, **kwargs)
        self.min_length = min_length

    def validate(self, value, schema=None):
        if len(str(value)) >= self.min_length:
            return value
        raise Exception(f"Must be at least {self.min_length} characters")

def demo_custom_validator():
    """Custom validation rules"""
    print("\n=== Custom Rules Demo ===")

    guard = Guard().use(ContainsTechnicalTerm())

    test_texts = [
        "Write a Python function to sort data",
        "Write something nice about cooking",
        "Create an API endpoint for authentication"
    ]

    for text in test_texts:
        try:
            guard.validate(text)
            print(f"[OK] {text[:40]}...")
        except Exception as e:
            print(f"[BLOCKED] {text[:40]}...")

def demo_structured_output():
    """Force structured output using Pydantic"""
    print("\n=== Structured Output Demo ===")

    from pydantic import BaseModel
    from typing import List

    class CodeReview(BaseModel):
        issues: List[str]
        suggestions: List[str]
        rating: int

    guard = Guard.for_pydantic(CodeReview)

    valid_response = '{"issues": ["Memory leak", "No error handling"], "suggestions": ["Add try-catch"], "rating": 6}'

    try:
        result = guard.validate(valid_response)
        print("[OK] Valid JSON structure")
        data = result.validated_output
        if isinstance(data, dict):
            print(f"    Rating: {data.get('rating', 'N/A')}")
            print(f"    Issues: {len(data.get('issues', []))}")
        else:
            print(f"    Output: {data}")
    except Exception as e:
        print(f"[ERROR] {e}")

def demo_length_validator():
    """Length validation"""
    print("\n=== Length Validation ===")

    guard = Guard().use(MinLength(min_length=20))

    texts = [
        "This is a short text",
        "This is a much longer text that should pass",
        "Hello world, this is a test message"
    ]

    for text in texts:
        try:
            guard.validate(text)
            print(f"[OK] Length: {len(text)} chars")
        except Exception as e:
            print(f"[SHORT] Length: {len(text)} chars")

def main():
    print("=" * 50)
    print("AI GUARDRAILS - Rules Enforcer")
    print("=" * 50)

    demo_custom_validator()
    demo_structured_output()
    demo_length_validator()

    print("\n" + "=" * 50)
    print("GUARDRAILS INSTALLED SUCCESSFULLY!")
    print("=" * 50)
    print("""
Key Features:
  - Custom validators (registered)
  - Pydantic schema validation
  - Structured JSON output
  - Input/output filtering

Docs: https://docs.guardrailsai.com/
    """)

if __name__ == "__main__":
    main()
