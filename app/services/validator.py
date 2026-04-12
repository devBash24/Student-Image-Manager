from __future__ import annotations

import re
from dataclasses import dataclass

def clean_text(text: str) -> str:
    # Remove newlines and extra spaces
    text = text.replace("\n", " ").strip()

    # Remove non-alphanumeric except spaces
    text = re.sub(r'[^A-Za-z0-9 ]', '', text)

    return text
def find_student_number(digits: str):
    candidates = []

    # Check all 10-digit windows
    for i in range(len(digits) - 9):
        chunk = digits[i:i+10]

        if re.match(r'^202\d(20|30|51)\d{4}$', chunk):
            candidates.append(chunk)

    return candidates[0] if candidates else None

def fix_ocr_errors(text: str) -> str:
    replacements = {
        "O": "0",
        "o": "0",
        "I": "1",
        "l": "1",
        "S": "5",
        "B": "8"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def extract_digits(text: str) -> str:
    return re.sub(r"\D", "", text)

def process_text(raw_text: str):

    # Fix OCR mistakes
    fixed = fix_ocr_errors(raw_text)

    # Extract digits
    digits = extract_digits(fixed)

    # Try exact match first
    if len(digits) == 10 and re.match(r'^202\d(20|30|51)\d{4}$', digits):
        return digits

    # Fallback: sliding window search
    result = find_student_number(digits)

    return result


@dataclass(frozen=True)
class ValidationResult:
    student_no: str | None
    pattern: str | None

    @property
    def is_valid(self) -> bool:
        return self.student_no is not None


class StudentNumberValidator:
    def __init__(self, patterns: list[str]) -> None:
        self.patterns = patterns

    def validate(self, text: str) -> ValidationResult:
        text = clean_text(text)
        result = process_text(text)
        if result:
            return ValidationResult(student_no=result, pattern=None)
        for pattern in self.patterns:
            match = re.search(pattern, text)
            if match:
                return ValidationResult(student_no=match.group(0), pattern=pattern)
        return ValidationResult(student_no=None, pattern=None)
