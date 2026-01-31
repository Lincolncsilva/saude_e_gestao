import re

def validar_cnpj(cnpj):
    """Valida formato e dígitos verificadores de um CNPJ."""
    cnpj = re.sub(r'\D', '', str(cnpj))
    
    if len(cnpj) != 14 or cnpj in [s * 14 for s in "0123456789"]:
        return False

    def calcular_digito(base, pesos):
        soma = sum(int(a) * b for a, b in zip(base, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    if int(cnpj[12]) != calcular_digito(cnpj[:12], pesos1):
        return False
    if int(cnpj[13]) != calcular_digito(cnpj[:13], pesos2):
        return False
    return True

def validar_positivo(valor):
    """Verifica se o valor é numérico e positivo."""
    try:
        return float(valor) >= 0
    except:
        return False

def validar_razao_social(nome):
    """Verifica se a Razão Social não está vazia."""
    return bool(nome and str(nome).strip())