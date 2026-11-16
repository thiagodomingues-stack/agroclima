import { useEffect, useState } from "react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid,
  ComposedChart, BarChart, Bar, Legend,
} from "recharts";
import "./App.css";

const API = "http://127.0.0.1:8000";

function useApi(path) {
  const [data, setData] = useState([]);
  const [erro, setErro] = useState(false);
  useEffect(() => {
    setErro(false);
    fetch(API + path)
      .then((r) => r.json())
      .then((d) => setData(Array.isArray(d) ? d : []))
      .catch(() => setErro(true));
  }, [path]);
  return { data, erro };
}

function Card({ titulo, children }) {
  return (
    <section className="card">
      <h2>{titulo}</h2>
      {children}
    </section>
  );
}

export default function App() {
  const [cultura, setCultura] = useState("cafe");
  const nome = cultura === "cafe" ? "café" : "milho";

  const alertas = useApi("/alertas");
  const clima = useApi("/clima?dias=30");
  const precos = useApi(`/precos?cultura=${cultura}&dias=120`);
  const corr = useApi(`/correlacao?cultura=${cultura}`);
  const safra = useApi("/safra");

  const safraCultura = safra.data.filter((s) =>
    s.cultura.toLowerCase().startsWith(nome.slice(0, 3))
  );

  return (
    <main>
      <h1>AgroClima Integrado</h1>
      <p className="sub">
        São João da Boa Vista (SP): clima, preço e safra em um só painel
      </p>

      <div className="abas">
        {["cafe", "milho"].map((c) => (
          <button
            key={c}
            className={c === cultura ? "ativo" : ""}
            onClick={() => setCultura(c)}
          >
            {c === "cafe" ? "Café" : "Milho"}
          </button>
        ))}
      </div>

      {alertas.erro && (
        <p className="erro">Backend fora do ar. Rode o uvicorn na pasta backend.</p>
      )}

      <Card titulo="Alertas">
        {alertas.data.length === 0 ? (
          <p>Sem alertas no momento.</p>
        ) : (
          alertas.data.map((a, i) => (
            <div key={i} className={a.tipo === "ação sugerida" ? "alerta destaque" : "alerta"}>
              <strong>{a.tipo}</strong> {a.data ? `(${a.data})` : ""} {a.descricao}
            </div>
          ))
        )}
      </Card>

      <div className="grade">
        <Card titulo={`Preço do ${nome} (${precos.data[0]?.unidade ?? ""})`}>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={precos.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="data" minTickGap={40} />
              <YAxis domain={["auto", "auto"]} />
              <Tooltip />
              <Line type="monotone" dataKey="preco" dot={false} stroke="#2f7d32" />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card titulo="Clima: últimos 30 dias e previsão">
          <ResponsiveContainer width="100%" height={260}>
            <ComposedChart data={clima.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="data" minTickGap={30} />
              <YAxis yAxisId="temp" unit="°" />
              <YAxis yAxisId="chuva" orientation="right" unit="mm" />
              <Tooltip />
              <Legend />
              <Bar yAxisId="chuva" dataKey="chuva_mm" name="Chuva (mm)" fill="#64b5f6" />
              <Line yAxisId="temp" dataKey="temp_max" name="Máx" stroke="#e53935" dot={false} />
              <Line yAxisId="temp" dataKey="temp_min" name="Mín" stroke="#1e88e5" dot={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </Card>

        <Card titulo={`Preço x chuva por mês (${nome})`}>
          <ResponsiveContainer width="100%" height={260}>
            <ComposedChart data={corr.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="mes" />
              <YAxis yAxisId="chuva" unit="mm" />
              <YAxis yAxisId="preco" orientation="right" domain={["auto", "auto"]} />
              <Tooltip />
              <Legend />
              <Bar yAxisId="chuva" dataKey="chuva_mm" name="Chuva (mm)" fill="#64b5f6" />
              <Line yAxisId="preco" dataKey="preco" name="Preço médio" stroke="#2f7d32" />
            </ComposedChart>
          </ResponsiveContainer>
        </Card>

        <Card titulo={`Produção de ${nome} em São João da Boa Vista (t)`}>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={safraCultura}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="ano" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="producao_t" name="Produção (t)" fill="#8d6e63" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </main>
  );
}