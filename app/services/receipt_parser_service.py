import re
from datetime import datetime
from decimal import Decimal, InvalidOperation


class ReceiptParserService:

    def parse(self, raw_text: str) -> dict:
        lines = [
            line.strip()
            for line in raw_text.splitlines()
            if line.strip()
        ]

        return {
            "merchant": self._extract_merchant(lines),
            "total": self._extract_total(lines),
            "date": self._extract_date(raw_text),
            "currency": "BRL",
            "items": self._extract_items(lines),
            "rawText": raw_text,
            "confidence": 0,
        }

    def _extract_merchant(self, lines: list[str]) -> str | None:
        """
        Tenta identificar o estabelecimento usando as primeiras
        linhas do recibo.
        """

        if not lines:
            return None

        ignored_patterns = [
            r"^\d+$",
            r"^CNPJ",
            r"^CPF",
            r"^R\$",
            r"^\d{2}/\d{2}/\d{2,4}$",
        ]

        for line in lines[:8]:
            if len(line) < 3:
                continue

            if any(re.search(pattern, line, re.IGNORECASE)
                   for pattern in ignored_patterns):
                continue

            # Evita linhas compostas apenas por números/símbolos
            if not re.search(r"[A-Za-zÀ-ÿ]", line):
                continue

            return line

        return None

    def _extract_total(self, lines: list[str]) -> float | None:
        """
        Procura valores próximos a palavras relacionadas ao total.
        """

        total_keywords = [
            "total",
            "valor total",
            "vl total",
            "vl.total",
            "vltotal",
            "valor a pagar",
            "total a pagar",
        ]

        for index, line in enumerate(lines):
            normalized = self._normalize(line)

            if any(keyword in normalized for keyword in total_keywords):
                # Primeiro tenta encontrar o valor na própria linha
                value = self._extract_money(line)

                if value is not None:
                    return value

                # Depois verifica as próximas linhas
                for next_line in lines[index + 1:index + 3]:
                    value = self._extract_money(next_line)

                    if value is not None:
                        return value

        return None

    def _extract_date(self, text: str) -> str | None:
        """
        Procura datas nos formatos:
        DD/MM/YYYY
        DD/MM/YY
        """

        matches = re.findall(
            r"\b(\d{2})/(\d{2})/(\d{2,4})\b",
            text,
        )

        for day, month, year in matches:
            try:
                if len(year) == 2:
                    year = f"20{year}"

                date = datetime(
                    int(year),
                    int(month),
                    int(day),
                )

                return date.date().isoformat()

            except ValueError:
                continue

        return None

    def _extract_items(self, lines: list[str]) -> list[dict]:
        """
        Primeira versão:
        tenta reconhecer linhas com quantidade + valores.

        Exemplos:
        2 UN 4,15 8,30
        1 10,00 10,00
        """

        items = []

        pattern = re.compile(
            r"""
            ^\s*
            (?P<quantity>\d+(?:[.,]\d+)?)
            \s*
            (?:UN|UND|UNID)?
            \s+
            (?P<unit_price>\d+[.,]\d{2})
            \s+
            (?P<total_price>\d+[.,]\d{2})
            \s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        )

        for line in lines:
            match = pattern.match(line)

            if not match:
                continue

            items.append({
                "name": None,
                "quantity": self._to_float(
                    match.group("quantity")
                ),
                "unitPrice": self._to_float(
                    match.group("unit_price")
                ),
                "totalPrice": self._to_float(
                    match.group("total_price")
                ),
            })

        return items

    def _extract_money(self, text: str) -> float | None:
        """
        Reconhece:
        70,47
        70.47
        R$ 70,47
        """

        matches = re.findall(
            r"(?:R\$\s*)?(\d{1,6}(?:[.,]\d{2}))",
            text,
        )

        if not matches:
            return None

        # Em linhas de total, normalmente o último valor
        # é o valor efetivamente total.
        value = matches[-1]

        return self._to_float(value)

    def _to_float(self, value: str) -> float | None:
        try:
            normalized = value.replace(".", "").replace(",", ".")

            # Caso original esteja no formato 70.47
            if "," not in value and "." in value:
                normalized = value

            return float(
                Decimal(normalized)
            )

        except (InvalidOperation, ValueError):
            return None

    def _normalize(self, text: str) -> str:
        return (
            text
            .lower()
            .replace("á", "a")
            .replace("à", "a")
            .replace("ã", "a")
            .replace("â", "a")
            .replace("é", "e")
            .replace("ê", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ô", "o")
            .replace("õ", "o")
            .replace("ú", "u")
        )