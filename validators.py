# As 27 Unidades Federativas do Brasil (26 estados + DF)
UFS_VALIDAS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}

UF_NOMES = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
    "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão",
    "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
    "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco",
    "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima",
    "SC": "Santa Catarina", "SP": "São Paulo", "SE": "Sergipe",
    "TO": "Tocantins",
}


def validar_uf(uf: str) -> str:
    """Normaliza e valida a UF. Retorna em maiúsculas ou lança ValueError."""
    if not uf:
        raise ValueError("UF é obrigatória.")

    uf_normalizada = uf.strip().upper()

    if len(uf_normalizada) != 2:
        raise ValueError(f"UF deve ter exatamente 2 letras (recebido: '{uf}').")

    if uf_normalizada not in UFS_VALIDAS:
        raise ValueError(
            f"UF '{uf_normalizada}' inválida. "
            f"Use uma das 27 UFs oficiais (ex: SP, RJ, MG)."
        )

    return uf_normalizada


def validar_pessoa(nome: str, cidade: str, estado: str) -> dict:
    """Valida e normaliza os campos de uma pessoa."""
    nome = (nome or "").strip()
    cidade = (cidade or "").strip()
    estado = (estado or "").strip()

    if not nome:
        raise ValueError("Nome é obrigatório.")
    if len(nome) > 150:
        raise ValueError("Nome deve ter no máximo 150 caracteres.")

    if not cidade:
        raise ValueError("Cidade é obrigatória.")
    if len(cidade) > 100:
        raise ValueError("Cidade deve ter no máximo 100 caracteres.")

    estado = validar_uf(estado)

    return {"nome": nome, "cidade": cidade, "estado": estado}