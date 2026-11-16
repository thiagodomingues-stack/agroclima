CREATE TABLE municipio (id SERIAL PRIMARY KEY, nome TEXT, lat NUMERIC, lon NUMERIC);
CREATE TABLE cultura (id SERIAL PRIMARY KEY, nome TEXT UNIQUE);
CREATE TABLE clima_diario (municipio_id INT REFERENCES municipio(id), data DATE,
  temp_min NUMERIC, temp_max NUMERIC, chuva_mm NUMERIC, PRIMARY KEY (municipio_id, data));
CREATE TABLE preco_diario (cultura_id INT REFERENCES cultura(id), data DATE,
  preco NUMERIC, unidade TEXT, PRIMARY KEY (cultura_id, data));
CREATE TABLE safra (municipio_id INT REFERENCES municipio(id), cultura_id INT REFERENCES cultura(id),
  ano INT, area_ha NUMERIC, producao_t NUMERIC, PRIMARY KEY (municipio_id, cultura_id, ano));
CREATE TABLE alerta (id SERIAL PRIMARY KEY, data DATE, cultura_id INT, tipo TEXT, descricao TEXT);

INSERT INTO municipio (nome, lat, lon) VALUES ('São João da Boa Vista', -21.9697, -46.7978);
INSERT INTO cultura (nome) VALUES ('café'), ('milho');