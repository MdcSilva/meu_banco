CREATE TABLE IF NOT EXISTS lancamentos (
    id BIGSERIAL PRIMARY KEY,
    data DATE NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('Entrada', 'Saída')),
    categoria TEXT NOT NULL,
    forma TEXT NOT NULL,
    descricao TEXT,
    valor NUMERIC(12, 2) NOT NULL CHECK (valor >= 0)
);

CREATE TABLE IF NOT EXISTS parcelas (
    id BIGSERIAL PRIMARY KEY,
    vencimento DATE NOT NULL,
    valor NUMERIC(12, 2) NOT NULL CHECK (valor >= 0),
    status TEXT NOT NULL DEFAULT 'ABERTO' CHECK (status IN ('ABERTO', 'PAGO')),
    descricao TEXT NOT NULL,
    pago_em DATE
);